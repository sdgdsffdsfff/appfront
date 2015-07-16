#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: LIPH
# Date: 20150709
import BaseHTTPServer, SocketServer, cgi
import shutil, zipfile, os
import httplib, urllib
import json
from os import curdir, sep, path
# File folder dir
dir_path = 'D:\\IntPassion\\Documents\\workspace\\Deal_uploadfile\\Project\\test\\liph'
dir_cfgfile = 'deploy_cfg.lst'
uploadhtml = '''<html><body>
<p>批量文件上传</p>
<form enctype="multipart/form-data" action="/" method="post">
<p>File: <input type="file" name="file1"></p>
<p>File: <input type="file" name="file2"></p>
<p>File: <input type="file" name="file3"></p>
<p>File: <input type="file" name="file4"></p>
<p>File: <input type="file" name="file5"></p>
<p><input type="submit" value="上传"></p>
</form>
</body></html>'''
def HttpConnectionInit(host = '192.168.1.3', port = 8080):
    return httplib.HTTPConnection(host, port)

def HttpConnectionClose(connection):
    connection.close()
class WebHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
           self.send_response(200)
           self.send_header('Content-Type', 'text/html; charset=utf-8')
           self.end_headers()
           self.wfile.write(uploadhtml)
           return
        try:
           f = open(curdir + sep + self.path)
           self.send_response(200)
           self.end_headers()
           self.wfile.write(f.read())
           f.close()
        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
    def do_POST(self):
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write('<Html>上传开始。<br/><br/>');
        self.wfile.write('客户端: %s<br/>' % str(self.client_address))
        conn  =  HttpConnectionInit()
        for field in form.keys():
            field_item = form[field]
            # self.wfile.write(' Field value： %s <br/>' % field)
            if field_item.filename:
                # Get the file name which not includes the dir
                name = path.split(field_item.filename)
                # The destination dir name
                des_fn = dir_path + sep + name[1]
                # fn=curdir+sep+field_item.filename
                self.wfile.write('目标文件路径：   %s <br/>' % (des_fn))
                if path.exists(field_item.filename) == 0:
                   self.wfile.write('文件 <a href="%s">%s</a> 不存在，无法上传。<br/>' % (field_item.filename, field_item.filename))
                elif path.splitext(field_item.filename)[1] <> '.zip':
                   self.wfile.write('文件 <a href="%s">%s</a> 不是zip压缩包，拒绝上传。<br/>' % (field_item.filename, field_item.filename)) 
                else:
                   # Judge whether the application exists or not
                   zfile = zipfile.ZipFile(field_item.filename, 'r')
                   for file in zfile.namelist():
                       #Judge whether the file is a dir or not (Application name is in the first dir
                       if file.endswith("/") and len(file.split('/'))==2:
                           self.wfile.write('Dir is %s <br/>' % file)
                           # Judge whether the application exists or not
                           appname = file.rstrip('/')
                           self.wfile.write('Application name is %s <br/>' % appname)
                           #Return the search result
                           url_ci = "/ci?name=" + appname + "&citype_name=APPLICATION"
                           conn.request(method = "GET",url = url_ci)
                           data_ci = json.loads(conn.getresponse().read())
                           self.wfile.write('Search result is %s <br/>' % len(data_ci))
                           if len(data_ci)<>0: #测试完要改成=
                               self.wfile.write('Application %s does not exist <br/>' % appname)
                               zfile.close()
                               HttpConnectionClose(conn)
                               self.wfile.write('</html>')
                               return 
                       else:                           
                           appname = path.split(file)[0].rstrip('/')
                           cfgfile_name = path.split(file)[1]
                           self.wfile.write('Appname is %s and config name is %s <br/>' % (appname,cfgfile_name))
                           #self.wfile.write(' %s <br/>' % cmp(cfgfile_name, 'deploy_config.lst'))
                           if cmp(cfgfile_name, 'deploy_config.lst') == -1:
                               file_open = zfile.open(file,'r')
                               #First line is application note
                               file_open.readline()
                               #Second line is application's attribute
                               file_open.readline()
                               ##Third line is component note
                               file_open.readline()
                               #Judge whether the application's component exists or not
                               comp_name = 0
                               for comp_info in file_open:
                                   #Since every line includes a component , we should exclude the repeated one.
                                   if comp_info.split(',')[0] <> comp_name:
                                       self.wfile.write('Component name is %s <br/>' % comp_info.split(',')[0])
                                       comp_name=comp_info.split(',')[0]
                                       #Return the search result
                                       url_ci = "/cirela?typename=APPCOMPSCOMP&targetname=" + comp_info.split(',')[0] + "&sourcename=" + appname
                                       conn.request(method = "GET",url = url_ci)
                                       data_ci = json.loads(conn.getresponse().read())
                                       self.wfile.write('Search result is %s <br/>' % len(data_ci))
                                       if len(data_ci) <> 0: #测试完要改成==
                                           self.wfile.write('Application %s \'s component %s does not exist <br/>' % (appname,comp_info.split(',')[0]))
                                           zfile.close()
                                           HttpConnectionClose(conn)
                                           self.wfile.write('</html>')
                                           return                                                                                 
                   #zfile.close()
                   #Prepare to upload zip file
                   file_data = field_item.file.read()
                   file_len = len(file_data)
                   del file_data
                   #============================================================
                   # shutil.copy(field_item.filename, des_fn)
                   # self.wfile.write('文件 <a href="%s">%s</a> 成功上传，尺寸为：%d bytes<br/>' % (field_item.filename, field_item.filename, file_len))
                   # # Decompress the upload file to the destination
                   # zfile = zipfile.ZipFile(des_fn, 'r')
                   # zfile.extractall(dir_path+sep)
                   # self.wfile.write('文件 %s 解压完毕<br/>' % des_fn)
                   #============================================================
                   # Based on the deploy_cfg.lst of every application , execute sql command 
                   for file in sorted(zfile.namelist(),reverse=True):
                       #Judge whether the file is a dir or not
                       self.wfile.write('file %s <br/>' % file)
                       zfile.extract(file,dir_path+sep)
                       #Just decompress  one application patchset for one time. Each tag is for a single patchset. 
                       if file.endswith("/") and len(file.split('/'))==2:
                           self.wfile.write('Dir is %s <br/>' % file)                                                                                                         
                           #zfile.extract(file,dir_path+sep)                           
                           # Get the config file
                           cfgfile = dir_path + sep + file + dir_cfgfile
                           fcfg = open(cfgfile,'r')
                           #First line is note
                           fcfg.readline()
                           #Second line is application's attribute
                           attr_lines = fcfg.readline().rstrip('\n')
                           for attr in attr_lines.split(','):
                               self.wfile.write('Attribute are %s : %s <br/>' % (attr_lines,attr))
                           #Third line is note
                           fcfg.readline()
                           #Remain is the info of components
                           for cfgline in fcfg:
                               self.wfile.write(' %s <br/>' % cfgline)
                           fcfg.close()
                           self.wfile.write('!!!!The app patchset\'s tag can be put here !!!!! <br/>')
                   zfile.close()
        HttpConnectionClose(conn)
        self.wfile.write('</html>')
                   
class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass
if __name__ == '__main__':
    server_address = ('0.0.0.0', 8080)
    httpd = ThreadingHTTPServer(server_address, WebHandler)
    print "Web Server On %s:%d" % server_address
    httpd.serve_forever()
