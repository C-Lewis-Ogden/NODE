#!/usr/bin/python3
import os,json,subprocess
import configparser
from flask import Flask,request,jsonify, redirect, url_for
from flask_cors import CORS, cross_origin
app = Flask(__name__)
app.run(ssl_context='adhoc')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
config = configparser.ConfigParser()
config.read('threatware.ini')
base = os.path.join(config['general']['rootdirectory'],'modules')
pythonpath = config['general']['pythonpath']
apiversion = config['general']['apiversion']
app.config['UPLOAD_FOLDER'] = config['general']['uploadfolder']
@app.route('/%s/modules/list'%apiversion)
def listModules():
	modules = []
	for module_name in os.listdir(base):
		current = os.path.join(base,module_name)
		if module_name[0] != '.' and os.path.isdir(os.path.join(base,module_name)):
			v_file = os.path.join(current,'VERSION')
			if os.path.isfile(v_file):
				v_file_h = open(v_file,"r")
				version = v_file_h.read()
				v_file_h.close()
			else:
				version = 'unknown'

		modules.append({'module':module_name,'version':version})
	return jsonify({'action':'listModules','result':modules}) 
@app.route('/%s/modules/<module_name>/config'%apiversion,methods = ['GET'])
def getConfig(module_name):
	current = os.path.join(base,module_name)
	c_file = os.path.join(current,'config.json')
	if os.path.isfile(c_file):
		c_file_h = open(c_file,"r")
		config = c_file_h.read()
		c_file_h.close()
	else:
		config = ''
	return jsonify({'action':'getConfig','module':module_name,'result':config})
@app.route('/%s/modules/<module_name>/config'%apiversion,methods = ['POST'])
def writeConfig(module_name):
	current = os.path.join(base,module_name)
	c_file = os.path.join(current,'config.json')
	c_file_h = open(c_file,"w")
	data = request.json["configuration"]
	c_file_h.write(str(data))
	c_file_h.close()
	return jsonify({'action':'writeConfig','module':module_name,'result':'OK'})  
@app.route('/%s/modules/<module_name>/run'%apiversion)
def runModule(module_name):
	current = os.path.join(base,module_name)
	m_file = os.path.join(current,'run.py')
	if os.path.isfile(m_file):
		module = subprocess.run([pythonpath, 'run.py'], stdout=subprocess.PIPE, cwd=current)
		output = module.stdout
	else:
		output = ''
	return jsonify({'action':'runModule','module':module_name,'result':output.decode('UTF-8')})
@app.route('/%s/modules/<module_name>/results'%apiversion)
def listResults(module_name):
	results = []
	current = os.path.join(base,module_name)
	for result_file in os.listdir(current):
		if result_file[-4:] == '.log':
			results.append({'file':result_file,'date':os.stat(current).st_ctime})
	return jsonify({'action':'listResults','module':module_name,'result':results})
@app.route('/%s/modules/<module_name>/results/<id>'%apiversion)
def showResults(module_name,id):
	current = os.path.join(base,module_name,id+'.log')
	r_file_h = open(current,"r")
	output = r_file_h.read()
	r_file_h.close()
	return jsonify({'action':'showResult','module':module_name,'result':output})
@app.route('/%s/system/install/<filename>'%apiversion,methods=['POST'])
def installModule(filename):
	file = request.files['file']
	file_path = os.path.join(app.config['UPLOAD_FOLDER'],filename)
	file.save(file_path)
	subprocess.run(['unzip',file_path ,'-d','/home/threatware/modules'])
	return jsonify({'action':'installModule','module':filename,'result':'OK'})
