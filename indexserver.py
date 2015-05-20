from http.server import BaseHTTPRequestHandler,HTTPServer
from os.path import abspath, join, isdir, exists
from os import listdir
import mimetypes

mimetypes.init()

PORT_NUMBER = 8080
BASE_PATH = abspath(".")
REPEAT_START = '<!-- repeat -->'
REPEAT_END = '<!-- end repeat -->'
 
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if(self.path == "/"):
            self.serve_index()
        else:
            self.serve_file()
        return

    def serve_index(self):
        self.send_response(200)
        self.send_header('Content-type','text/html')
        self.end_headers()
        
        header, footer, row = read_template()
        self.write_string(header)
        for file in listdir("."):
            if(isdir(file) and file[0] != '.'):
                self.write_string(row.format(href=file, text=file, time='2015-01-01'))
        self.write_string(footer)  

    def serve_file(self):
        fileName = "." + self.path
        if(self.can_serve(fileName)):
            self.send_response(200)
            self.send_header('Content-type', mimetypes.guess_type(self.path)[0])
            self.end_headers()
            file = open("." + self.path, "rb")
            self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.write_string('Not found: ' + self.path)  
            
        
    def write_string(self, str):
        self.wfile.write(bytes(str, "utf-8"))
        
    def can_serve(self, file):
        if(not exists(file) or isdir(file)):
            return False
        
        abs_filename = abspath(file)
        return abs_filename[0:len(BASE_PATH)] == BASE_PATH
        
def read_template():
    f = open('./.template/template.html', 'r')  
    template = f.read()
    
    first_index = template.index(REPEAT_START)
    second_index = template.index(REPEAT_END)
    
    header = template[:first_index]
    footer = template[second_index + len(REPEAT_END):]
    row = template[first_index + len(REPEAT_START): second_index]
    
    return (header, footer, row)

try:
    server = HTTPServer(('', PORT_NUMBER), Handler)
    print ('Started httpserver on port ' , PORT_NUMBER)

    server.serve_forever()

except KeyboardInterrupt:
    print ('^C received, shutting down the web server')
    server.socket.close()
