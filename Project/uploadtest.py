#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author: LIPH
# Date: 20150709
import BaseHTTPServer, SocketServer, cgi
import shutil, zipfile, os
import httplib, urllib
import json
import time
import string
from os import curdir, sep, path
# File folder dir
dir_path = 'D:\\IntPassion\\Documents\\workspace\\Deal_uploadfile\\Project\\test\\liph'
dir_cfgfile = 'deploy_cfg.lst'
#Define the fixed family_ids in CMDB
ENVIR_FCIT = 'FCIT00000017'
APP_FCIT = 'FCIT00000018'
APPPATCH_FCIT = 'FCIT00000019'
COMP_FCIT = 'FCIT00000020'
COMPPATCH_FCIT = 'FCIT00000021'
COMPITEM_FCIT = 'FCIT00000022'
COMPDEPLOY_FCIT = 'FCIT00000023'
COMPCONFIG_FCIT = 'FCIT00000024'
PATCHITEM_FCIT = 'FCIT00000025'
APPPATCH_VERSION_FCAT = 'FCAT00000122'
APPPATCH_BASE_FCAT = 'FCAT00000123'
APPPATCH_RESP_FCAT = 'FCAT00000124'
APPPATCH_FLAG_FCAT = 'FCAT00000125'
APPPATCH_PUBDATE_FCAT = 'FCAT00000126'
COMPPATCH_VERSION_FCAT = 'FCAT00000127'
PATCHITEM_SEQ_FCAT = 'FCAT00000128'
COMPITEM_OWNER_FCAT = 'FCAT00000129'
COMPITEM_PERMIS_FCAT = 'FCAT00000130'
COMPITEM_URI_FCAT = 'FCAT00000131'
COMPITEM_TARGETDIR_FCAT = 'FCAT00000132'
COMPITEM_MD5_FCAT = 'FCAT00000133'
COMPITEM_FETURE_FCAT = 'FCAT00000134'
COMPITEM_VERSION_FCAT = 'FCAT00000135'
COMPITEM_DEPLOY_FCAT = 'FCAT00000136'
APPOWNCOMP_FCRT = 'FCRT00000018'
COMPHASITEM_FCRT = 'FCRT00000026'

######################################################################################################
uploadhtml = '''<html><body>
<p>批量文件上传</p>
<form enctype="multipart/form-data" action="/" method="post">
<p>File: <input type="file" name="file1"></p>
<p>File: <input type="file" name="file2"></p>
<p>File: <input type="file" name="file3"></p>
<p>File: <input type="file" name="file4"></p>
<p>File: <input type="file" name="file5"></p>
<label><input name="flag_todeploy" type="checkbox" value="0" />正式上线 </label>
<label><input name="flag_todeploy" type="checkbox" value="1" />预上线 </label>
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
        try:
           form = cgi.FieldStorage(fp=self.rfile, headers=self.headers, environ={'REQUEST_METHOD':'POST', 'CONTENT_TYPE':self.headers['Content-Type'], })
           self.send_response(200)
           self.send_header('Content-Type', 'text/html; charset=utf-8')
           self.end_headers()
           self.wfile.write('<Html>上传开始。<br/><br/>')        
           self.wfile.write('客户端: %s<br/>' % str(self.client_address))
           #Set the deploy flag based on the checkbox
           deploy_flag = form['flag_todeploy'].value
           self.wfile.write('预上线标志: %s<br/>' % deploy_flag)
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
                          self.wfile.write('#####################Current file is %s################### <br/>' % (file))
                          #Judge whether the file is a dir or not (Application name is in the first dir
                          if file.endswith("/") and len(file.split('/'))==2:
                              # Judge whether the application exists or not
                              appname = file.rstrip('/')
                              self.wfile.write('Application name is %s <br/>' % appname)
                              #Return the search result
                              url_ci = "/ci?name=" + appname + "&type_fid=" + APP_FCIT
                              conn.request(method = "GET",url = url_ci)
                              data_ci = json.loads(conn.getresponse().read())
                              self.wfile.write('Search result is %s <br/>' % len(data_ci))
                              if len(data_ci)==0: #测试完要改成==
                                  self.wfile.write('Application %s does not exist <br/>' % appname)
                                  zfile.close()
                                  HttpConnectionClose(conn)
                                  self.wfile.write('</html>')
                                  return 
                          else:                           
                              #====================================================
                              # appname = path.split(file)[0].rstrip('/')
                              # cfgfile_name = path.split(file)[1]
                              # self.wfile.write('Appname is %s and config name is %s <br/>' % (appname,cfgfile_name))
                              #====================================================                           
                              #Through the deploy config file, judge whether the basis patchset and component exist or not
                              if file == dir_cfgfile:
                                  file_open = zfile.open(file,'r')
                                  #First line is note
                                  file_open.readline()                              
                                  #Judge whether the patchset exists or not, whether the application's basis version and component exist or not
                                  patchset_name = 0
                                  basis_version = 0
                                  comp_name = 0
                                  for comp_info in file_open:
                                      #Since every line includes a patchset basis , we should exclude the repeated one.
                                      if comp_info.split(',')[0] <> patchset_name:
                                          patchset_name = comp_info.split(',')[0]
                                          self.wfile.write('The Patchset to deploy is %s <br/>' % (patchset_name))
                                          #Return the search result
                                          url_ci = "/ci?type_fid=" + APPPATCH_FCIT + "&name=" + patchset_name
                                          conn.request(method = "GET",url = url_ci)
                                          data_ci = json.loads(conn.getresponse().read())
                                          self.wfile.write('Search result is %s <br/>' % len(data_ci))
                                          if len(data_ci) <>0: #测试完要改成<>0
                                              self.wfile.write('Patchset %s has existed <br/>' % (patchset_name))
                                              zfile.close()
                                              HttpConnectionClose(conn)
                                              self.wfile.write('</html>')
                                              return                           
                                      
                                      #Since every line includes a patchset basis , we should exclude the repeated one.
                                      if comp_info.split(',')[1] <> "" and comp_info.split(',')[1] <> basis_version:
                                          basis_version = comp_info.split(',')[1]
                                          self.wfile.write('The basis of Patchset %s is %s <br/>' % (comp_info.split(',')[0],basis_version)) 
                                          #Return the search result
                                          url_ci = "/ci?type_fid=" + APPPATCH_FCIT + "&name=" + basis_version
                                          conn.request(method = "GET",url = url_ci)
                                          data_ci = json.loads(conn.getresponse().read())
                                          self.wfile.write('Search result is %s <br/>' % len(data_ci))
                                          if len(data_ci) <> 0: #测试完要改成==
                                              self.wfile.write('Patchset basis %s does not exist <br/>' % (basis_version))
                                              zfile.close()
                                              HttpConnectionClose(conn)
                                              self.wfile.write('</html>')
                                              return                           
                                      
                                      #Since every line includes a component , we should exclude the repeated one.
                                      if comp_info.split(',')[3] <> comp_name:
                                          patchset_name = comp_info.split(',')[0]
                                          appname = patchset_name.split('_')[0]
                                          comp_name=comp_info.split(',')[3]
                                          self.wfile.write('Application is %s and Component name is %s <br/>' % (appname,comp_name))                                       
                                          #Return the search result
                                          url_ci = "/cirela?type_fid=" + APPOWNCOMP_FCRT + "&targetname=" + comp_name + "&sourcename=" + appname
                                          conn.request(method = "GET",url = url_ci)
                                          data_ci = json.loads(conn.getresponse().read())
                                          self.wfile.write('Search result is %s <br/>' % len(data_ci))
                                          if len(data_ci) == 0: #测试完要改成==
                                              self.wfile.write('Application %s \'s component %s does not exist <br/>' % (appname,comp_name))
                                              zfile.close()
                                              HttpConnectionClose(conn)
                                              self.wfile.write('</html>')
                                              return                                                                                 
                      self.wfile.write('--------------------------------Judge END----------------------------------<br/>')
                      #============================================================
                      # #Prepare to upload zip file
                      # file_data = field_item.file.read()
                      # file_len = len(file_data)
                      # del file_data
                      # shutil.copy(field_item.filename, des_fn)
                      # self.wfile.write('文件 <a href="%s">%s</a> 成功上传，尺寸为：%d bytes<br/>' % (field_item.filename, field_item.filename, file_len))
                      # # Decompress the upload file to the destination
                      # zfile = zipfile.ZipFile(des_fn, 'r')
                      # zfile.extractall(dir_path+sep)
                      # self.wfile.write('文件 %s 解压完毕<br/>' % des_fn)
                      #============================================================
                      # Based on the deploy_cfg.lst of every application , execute sql command 
                      for file in sorted(zfile.namelist(),reverse=True):
                          if file <> dir_cfgfile:
                              #Judge whether the file is a dir or not                                         
                              self.wfile.write('file %s <br/>' % file)                                        
                              zfile.extract(file,dir_path+sep)                                                
                              #Just decompress  one application patchset for one time. Each tag is for a singl
                              if file.endswith("/") and len(file.split('/'))==2:                              
                                  self.wfile.write('Dir is %s <br/>' % file)                                  
                                  #zfile.extract(file,dir_path+sep)                                                                                                                                         
                                  self.wfile.write('!!!!The app patchset\'s tag can be put here !!!!! <br/>') 
                          else:
                              # Get the config file                                                       
                              fcfg = open(file,'r')                                                    
                              #First line is note                                                         
                              fcfg.readline()
                              #Add the application patchset / application attribute / component / component attribute
                              patchset_name = 0
                              basis_version = 0
                              comp_name = 0
                              for comp_info in fcfg:
                                  #Since every line includes an application and its patchset basis , we should exclude the repeated one.
                                  #Insert new application patchset ci, then build the relation between the application and the applicaiton patchset
                                  #Insert new patch_base ci_attribute
                                  if comp_info.split(',')[0] <> patchset_name:
                                      patchset_name = comp_info.split(',')[0]
                                      self.wfile.write('The Patchset to deploy is %s <br/>' % (patchset_name))
                                      #Insert the patchset info
                                      url_ci = "/ci?ci_type_fid=" + APPPATCH_FCIT + "&name=" + patchset_name
                                      conn.request(method = "POST", url = url_ci)
                                      ci_app_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI return family_id is %s <br/>' % ci_app_fid)
                                      appname = patchset_name.split('_')[0]
                                      #Return the family_id of the application
                                      url_ci = "/ci?name=" + appname + "&type_fid=" + APP_FCIT
                                      conn.request(method = "GET",url = url_ci)
                                      data_ci = json.loads(conn.getresponse().read())
                                      self.wfile.write('----The APP CI return family_id is %s <br/>' % data_ci[0]['FAMILY_ID'])
                                      #Insert the relation between the application and the application patchset
                                      url_ciattr = "/cirela?source_fid=" + data_ci[0]['FAMILY_ID'] + "&target_fid=" + ci_app_fid + "&relation=COMPOSITION"
                                      conn.request(method = "POST",url = url_ciattr)
                                      cirela_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid)
                                      
                                      #Insert attribute : version
                                      url_ciattr = "/ciattr?ci_fid=" + ci_app_fid + "&ci_attrtype_fid=" + APPPATCH_VERSION_FCAT + "&value=" + patchset_name[(len(appname)+1):]
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      
                                      basis_version = comp_info.split(',')[1]
                                      patch_resp = comp_info.split(',')[2]
                                      self.wfile.write('The basis of Patchset %s is %s, and %s is responsible for it. <br/>' % (patchset_name,basis_version,patch_resp)) 
                                      #Insert the attribute basis_version
                                      url_ciattr = "/ciattr?ci_fid=" + ci_app_fid + "&ci_attrtype_fid=" + APPPATCH_BASE_FCAT + "&value=" + basis_version
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      
                                      #Insert the attribute patchset_responsible
                                      url_ciattr = "/ciattr?ci_fid=" + ci_app_fid + "&ci_attrtype_fid=" + APPPATCH_RESP_FCAT + "&value=" + patch_resp
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      
                                      #Insert the attribute: flag_todeploy
                                      url_ciattr = "/ciattr?ci_fid=" + ci_app_fid + "&ci_attrtype_fid=" + APPPATCH_FLAG_FCAT + "&value=" + deploy_flag
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      
                                      #Insert the attribute: patch_pub_date
                                      url_ciattr = "/ciattr?ci_fid=" + ci_app_fid + "&ci_attrtype_fid=" + APPPATCH_PUBDATE_FCAT + "&value=" + time.strftime("%Y%m%d%H%M%S", time.localtime())
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      
                                  #Insert new component patchset ci, then build the relation between the application patchset and the component patchset
                                  if comp_info.split(',')[3] <> comp_name:
                                      item_seqid = 0
                                      comp_name = comp_info.split(',')[3] 
                                      appname = patchset_name.split('_')[0]                                                                   
                                      self.wfile.write('The component of application %s is %s. <br/>' % (appname,comp_name))
                                      #Insert the component
                                      url_ci = "/ci?ci_type_fid=" + COMPPATCH_FCIT + "&name=" + patchset_name
                                      conn.request(method = "POST", url = url_ci)
                                      ci_comp_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI return family_id is %s <br/>' % ci_comp_fid)
                                      #Insert the attribute : component version
                                      url_ciattr = "/ciattr?ci_fid=" + ci_comp_fid + "&ci_attrtype_fid=" + COMPPATCH_VERSION_FCAT + "&value=" + patchset_name[(len(appname)+1):]
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                      #Insert the relation between the application patchset and the component patchset
                                      url_cirela = "/cirela?source_fid=" + ci_app_fid + "&target_fid=" + ci_comp_fid + "&relation=COMPOSITION"
                                      conn.request(method = "POST",url = url_cirela)
                                      cirela_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid)
                                      #Insert the relation between the application component and the component patchset
                                      #Get the family_id of the application component                                   
                                      url_ci = "/cirela?type_fid=" + APPOWNCOMP_FCRT + "&targetname=" + comp_name + "&sourcename=" + appname
                                      conn.request(method = "GET",url = url_ci)
                                      data_ci = json.loads(conn.getresponse().read())
                                      component_fid = data_ci[0]['TARGET_FID']
                                      url_cirela = "/cirela?source_fid=" + component_fid + "&target_fid=" + ci_comp_fid + "&relation=REFERENCE"
                                      conn.request(method = "POST",url = url_cirela)
                                      cirela_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid)
                                  
                                  #Insert the patch_item ci , the component item ci; then build the relation between the application component and the component patchset, the relation between the application component and the component item
                                  item_uri = comp_info.split(',')[5]
                                  item_seqid = item_seqid + 1
                                  #Get the item name
                                  if  item_uri.find('\\')  >=0:                                   
                                      patchitem = item_uri.split('\\')[len(item_uri.split('\\'))-1]
                                  elif item_uri.find('/')  >=0:  
                                      patchitem = item_uri.split('/')[len(item_uri.split('/'))-1]
                                  else:
                                      patchitem = item_uri
                                  #Insert the patch_item ci and its attribute
                                  url_ci = "/ci?ci_type_fid=" + PATCHITEM_FCIT + "&name=" + patchitem
                                  conn.request(method = "POST", url = url_ci)
                                  ci_patchitem_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI return family_id is %s <br/>' % ci_patchitem_fid)
                                  url_ciattr = "/ciattr?ci_fid=" + ci_patchitem_fid + "&ci_attrtype_fid=" + PATCHITEM_SEQ_FCAT + "&value=" + str(item_seqid)
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)                        
                                  #Build the relation between the component patchset and the patch_item
                                  url_cirela = "/cirela?source_fid=" + ci_comp_fid + "&target_fid=" + ci_patchitem_fid + "&relation=COMPOSITION"
                                  conn.request(method = "POST",url = url_cirela)
                                  cirela_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid) 
                                  
                                  #Insert the component item ci and its attribute
                                  url_ci = "/ci?ci_type_fid=" + COMPITEM_FCIT + "&name=" + patchitem
                                  conn.request(method = "POST", url = url_ci)
                                  ci_compitem_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI return family_id is %s <br/>' % ci_compitem_fid)
                                  
                                  #Set item's attributes
                                  item_target = comp_info.split(',')[6]
                                  item_owner = comp_info.split(',')[7]
                                  item_permission = comp_info.split(',')[8]
                                  item_md5 = comp_info.split(',')[9]
                                  item_method = comp_info.split(',')[10]
                                  item_feture = comp_info.split(',')[11]
                                  item_version = patchset_name[(len(appname)+1):]
                                  #Insert item's attribute: owner
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_OWNER_FCAT + "&value=" + item_owner
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: permission
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_PERMIS_FCAT + "&value=" + item_permission
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: URI
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_URI_FCAT + "&value=" + item_uri
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s %s <br/>' % (ciattr_fid,item_uri))
                                  #Insert item's attribute: target_dir
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_TARGETDIR_FCAT + "&value=" + item_target
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: MD5
                                  if item_md5 <> "" :
                                      url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_MD5_FCAT + "&value=" + item_md5
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: feture point
                                  if item_feture <> "" :
                                      url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_FETURE_FCAT + "&value=" + item_feture
                                      conn.request(method = "POST",url = url_ciattr)
                                      ciattr_fid = conn.getresponse().read()
                                      self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: version
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_VERSION_FCAT + "&value=" + item_version
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
                                  #Insert item's attribute: deploy method
                                  url_ciattr = "/ciattr?ci_fid=" + ci_compitem_fid + "&ci_attrtype_fid=" + COMPITEM_DEPLOY_FCAT + "&value=" + item_method
                                  conn.request(method = "POST",url = url_ciattr)
                                  ciattr_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI ATTRIBUTE return family_id is %s <br/>' % ciattr_fid)
   
                                  #Build the relation between the application component and the component item, the relation between the patch_item and the component item
                                  url_cirela = "/cirela?source_fid=" + ci_patchitem_fid + "&target_fid=" + ci_compitem_fid + "&relation=COMPOSITION"
                                  conn.request(method = "POST",url = url_cirela)
                                  cirela_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid) 
                                  #Since the "application component" always refers to the latest component item, we should delete the older reference relationship firstly.
                                  url_ciattr = "/ciattr?type_fid=" + COMPITEM_TARGETDIR_FCAT + "&value=" + item_target
                                  conn.request(method = "GET",url = url_ciattr)
                                  data_ciattr = json.loads(conn.getresponse().read()) 
                                  for item_attr in data_ciattr:
                                      url_cirela = "/cirela?source_fid=" + component_fid + "&target_fid=" + item_attr['CI_FID'] + "&type_fid=" + COMPHASITEM_FCRT
                                      conn.request(method = "GET",url = url_cirela)
                                      data_cirela = json.loads(conn.getresponse().read())
                                      if len(data_cirela) <> 0:
                                          url_cirela = "/cirela?fid=" + data_cirela['FAMILY_ID'] + "&i_change_log=nextversion" + item_version
                                          conn.request(method = "DELETE",url = url_cirela)
                                          cirela_del = conn.getresponse().read()
                                          self.wfile.write('***Have deleted %s relations <br/>' % cirela_del) 
                                   #Build the new relation
                                  url_cirela = "/cirela?source_fid=" + component_fid + "&target_fid=" + ci_compitem_fid + "&relation=REFERENCE"
                                  conn.request(method = "POST",url = url_cirela)
                                  cirela_fid = conn.getresponse().read()
                                  self.wfile.write('----The CI RELATION return family_id is %s <br/>' % cirela_fid) 
                                          
                              fcfg.close()                                
   
                      zfile.close()
           HttpConnectionClose(conn)
           self.wfile.write('</html>')
           
        except Exception as e:
           self.send_error(500, 'Error: %s failed: %s' % (self.__class__.__name__,e)) 
                   
class ThreadingHTTPServer(SocketServer.ThreadingMixIn, BaseHTTPServer.HTTPServer): pass
if __name__ == '__main__':
    server_address = ('0.0.0.0', 8080)
    httpd = ThreadingHTTPServer(server_address, WebHandler)
    print "Web Server On %s:%d" % server_address
    httpd.serve_forever()
