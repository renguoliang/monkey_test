#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ftplib import FTP
import re
import os
import logging
import sys

def ftpconnect(host, username, password):
    ftp = FTP()
    # ftp.set_debuglevel(2)
    ftp.connect(host, 21)
    ftp.login(username, password)
    return ftp

#从ftp下载文件
def download_apk(ftp, remotepath, localpath):
    bufsize = 1024
    fp = open(localpath, 'wb')
    ftp.retrbinary('RETR ' + remotepath, fp.write, bufsize)
    ftp.set_debuglevel(0)
    fp.close()

def get_ftp_apk(prj_info):
    #链接FTP
    try:
        ftp = ftpconnect(prj_info["url"],prj_info["username"],prj_info["password"])
    except:
        logging.error("FTP connected failed")
        sys.exit(-1)
    ftp.dir(None, open('result', 'wb').write)
    result = open('result', 'rb').read()
    if "folder_re" in prj_info:
        last_apk_path = sorted(re.findall(prj_info["folder_re"],result),reverse=True)[0]
    else:
        last_apk_path = prj_info["apk_path"]
    ftp.cwd(last_apk_path)
    ftp.dir(None, open('result2', 'wb').write)
    result2 = open('result2','rb').read()
    filename = sorted(re.findall(prj_info["apk_re"], result2),reverse=True)[0]
    saved_path = "apks/" + prj_info["name"]+"/"
    #如果路径不存才，创建路径
    if not os.path.isdir(saved_path):
        os.mkdir(saved_path)
    logging.info("Find %s(%s), downloading..." % (filename, last_apk_path))
    #下载apk
    download_apk(ftp,filename,saved_path+filename)
    ftp.quit()
    apk_path = saved_path+filename
    return apk_path
