from http.server import BaseHTTPRequestHandler,HTTPServer
from os.path import abspath, join, isdir, exists
from os import listdir
from sys import argv
from datetime import datetime

import re
import mimetypes

mimetypes.init()

PORT_NUMBER = 8000
REPEAT_START = '<!-- repeat -->'
REPEAT_END = '<!-- end repeat -->'

base_path = abspath('.')
 
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path == '/'):
            self.serve_index()
        elif(self.path[0:10] == '/.template'):
            self.serve_file('.')
        else:
            self.serve_file(base_path)
        return

    def serve_index(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()

        header, footer, row = read_template()
        self.write_string(header)
        for file in listdir(base_path):
            if(isdir(join(base_path, file)) and file[0] != '.'):
                parts = file_parts(file)
                self.write_string(row.format(href=parts['href'], branch=parts['branch'], build=parts['build'], time=parts['time']))
        self.write_string(footer)  

    def serve_file(self, basePath):
        fileName = basePath + self.path
        if(self.can_serve(fileName)):
            self.send_response(200)
            self.send_header('Content-type', mimetypes.guess_type(self.path)[0])
            self.end_headers()
            file = open(fileName, "rb")
            self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.write_string('Not found: ' + self.path)  
        
    def write_string(self, str):
        self.wfile.write(bytes(str, 'utf-8'))
        
    def can_serve(self, file):
        if not exists(file) or isdir(file):
            return False
        if self.path[0:10] == '/.template':
            return True
        abs_filename = abspath(file)
        return abs_filename[0:len(base_path)] == base_path
        
def read_template():
    f = open('./.template/template.html', 'r')  
    template = f.read()
    
    first_index = template.index(REPEAT_START)
    second_index = template.index(REPEAT_END)
    
    header = template[:first_index]
    footer = template[second_index + len(REPEAT_END):]
    row = template[first_index + len(REPEAT_START): second_index]
    
    return (header, footer, row)

def file_parts(file):
    parts = {}
    parts['file'] = file
    parts['href'] = './' + file
    m = re.search('([0-9]{4})([0-9]{2})([0-9]{2})T([0-9]{2})([0-9]{2})([0-9]{2})_(.+)_(.+)', file)
    dt = datetime(int(m.group(1)),int(m.group(2)),int(m.group(3)),int(m.group(4)),int(m.group(5)),int(m.group(6)))

    parts['branch'] = m.group(7)
    parts['build'] = m.group(8)
    parts['time'] = dt.strftime('%Y-%m-%d %H:%M:%S')

    return parts

def print_help():
    print('Usage:')
    print('    python3 indexserver.py <path_to_build_dir> [port]')
    print('')
    print('    The path is mandatory, the port defaults to 8000')

if len(argv) < 2:
    print_help()
    exit(1)

base_path = abspath(argv[1])
port = PORT_NUMBER
if len(argv) > 2:
    port = int(argv[2])

try:
    server = HTTPServer(('', port), Handler)
    print('Serving basepath        :' + base_path)
    print('Started serving on port :' + str(port))

    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
