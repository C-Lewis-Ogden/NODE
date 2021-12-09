#!/usr/bin/python3
import socket, threading, sys, os, re, json

# Open the Config.JSON file that contains some initializing information for the script
f = open('config.json')
config = json.load(f)
f.close()

# Taking the IP address to scan from the Config.JSON file
# By default, this is set to scan itself using 127.0.0.1 as an address
ip = config['address'] 
threads = []
open_ports = {}

# Creating the HTML table data
table_header_html="<tr><th>Open Ports</th></tr>"
table_data_html=""

# A function that accepts an IP address, a port number, and an array of ports
# This function will open a socket and attempt a connection to the provided IP on the provided port
# The result of the connection attempt is stored in the array of ports
def try_port(ip, port, open_ports):

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(5)
    result = sock.connect_ex((ip, port))

    if result == 0:
        open_ports[port] = 'open'
        return True
    else:
        open_ports[port] = 'closed'
        return None

# A function that accepts an IP address
# This function will create a thread using the try_port function and add it to an array of threads
# It then loops through the range of ports provided, starting each thread
# The array of ports is the checked and any open ports are added to the HTML table
def scan_ports(ip):
    
    table_data=""
    
    for port in range(0, 65535):
        thread = threading.Thread(target=try_port, args=(ip, port, open_ports))
        threads.append(thread)

    for i in range(0, 65535):
        threads[i].start()

    for i in range(0, 65535):
        threads[i].join()

    for i in range (0, 65535):
        if open_ports[i] == 'open':
            table_data += "<tr><td>%s</td></tr>"%str(i)
            
    return table_data

# Calling the scan_port function to run the above code
try:
    table_data_html = scan_ports(ip)
    
except KeyboardInterrupt:
    sys.exit()

except socket.gaierror:
    sys.exit()

except socket.error:
    sys.exit()

# Create the HTML statement for the output
html_output = "<table>%s%s</table>"%(table_header_html,table_data_html)

# Check for the next available number in the log file naming convention
log_count = 1
while os.path.exists("output_%s.log"%log_count):
    log_count += 1  

# Open the log file and write the HTML statement to the log file and console
f = open('output_%s.log'%log_count,'w')
f.write(html_output)
f.close()
print(html_output)
