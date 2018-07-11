#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import socket
import urllib2
import re
import datetime
import subprocess
import shutil
import logging
from HTMLParser import HTMLParser

# 设置连接最大时长
socket.setdefaulttimeout(10)


class MyHTMLParser(HTMLParser):
    def __init__(self, name_re, datetime_re):
        HTMLParser.__init__(self)
        # _name_re为文件（夹）名正则，_datetime_re为修改日期正则，二者均为传入参数
        self._name_re = name_re
        self._datetime_re = datetime_re
        # _tags为需要抓取的tag
        self._tags = ("table", "tr", "th", "td")
        # _stack用于存tag堆栈
        self._stack = []
        # _name用于存文件（夹）名，_datetime用于存修改时间
        self._name = ""
        self._datetime = ""
        # _data用于存抓取到的数据，Key为文件（夹）名，Value为修改时间
        self._data = {}

    def handle_starttag(self, tag, attrs):
        # 如果起始tag在_tags中，则入栈
        if tag in self._tags:
            self._stack.append(tag)

    def handle_endtag(self, tag):
        # 如果终止tag在_tags中，则出栈
        if tag in self._tags:
            self._stack.pop()

    def handle_data(self, data):
        # 如果栈内有元素（即处于表格中），且栈内无"th"（即不处于标题中），则进行数据处理
        if self._stack and "th" not in self._stack:
            # 如果_name和_datetime均不为空，则表示抓到一条完整数据，将其写入_data，并置_name和_datetime为空
            if self._name and self._datetime:
                self._data[self._name] = self._datetime
                self._name = ""
                self._datetime = ""
            # 如果data匹配对应的正则规则，则将其赋值给_name或_datetime
            if re.match(self._name_re, data):
                self._name = data.strip()
            if re.match(self._datetime_re, data):
                self._datetime = datetime.datetime.strptime(data.strip(), "%Y-%m-%d %H:%M")

    def get_data(self):
        # 将_data按修改时间先后排序，最新的在前
        data = sorted(self._data.items(), key=lambda d: d[1], reverse=True)
        # 排序后的data为一个list，每个元素是一个tuple，值为(name, datetime)
        return data


def get_latest_folder(prj_info):
    try:
        # 请求URL，并抓取文件夹名和修改日期的数据；如果抓取失败，则结束运行
        content = urllib2.urlopen(prj_info["url"]).read()
        parser = MyHTMLParser(prj_info["folder_re"], prj_info["datetime_re"])
        parser.feed(content)
        data = parser.get_data()
        parser.close()
    except Exception as e:
        logging.warning(e)
        return None
    # 如果抓取的数据为空，则结束运行
    if not data:
        logging.warning("Error: there's no folders in %s" % prj_info["url"])
        return None
    return data


def get_latest_apk(folder_data, prj_info):
    # 从data中取最新的文件夹，并从中取apk文件；如果找不到apk文件，则从次新的文件夹中取，直到取到为止
    for item in folder_data:
        apk_path = prj_info["url"] + item[0] + prj_info["inner_path"]
        # 请求apk_path，并抓取apk文件名和修改日期的数据；如果抓取失败，可能是该次打包存在问题，则访问次新文件夹
        try:
            content = urllib2.urlopen(apk_path).read()
            parser = MyHTMLParser(prj_info["apk_re"], prj_info["datetime_re"])
            parser.feed(content)
            data = parser.get_data()
            parser.close()
        except urllib2.HTTPError as e:
            if e.code == 404:
                logging.warning("there's no apk file in %s, maybe an unsuccessful build" % apk_path)
            else:
                logging.warning(e)
            continue
        except Exception as e:
            logging.warning(e)
            continue
        # 找到所有符合APK_RE的包
        apk_list = []
        for apk_item in data:
            apk_list.append(apk_path + apk_item[0])
        # 如果没有符合的apk包，可能是该次打包存在问题，则访问次新文件夹
        if not apk_list:
            logging.warning("there's no matched apk file in %s, maybe an unsuccessful build" % apk_path)
            continue
        return True, apk_list
    return False, None


def download_apk(apk_list, prj_ver, prj_info):
    # 如果路径不存在，先创建路径
    saved_path = "apks/" + prj_ver
    if not os.path.isdir(saved_path):
        os.mkdir(saved_path)
    # 下载apk_list中的apk包
    for apk_url in apk_list:
        # 拆分出apk包的文件名，从而得到目标路径
        apk_name = apk_url.split("/")[-1]
        file_path = saved_path + "/" + apk_name
        # 拆分出文件夹名
        folder_name = apk_url[len(prj_info["url"]):].split("/")[0]
        # 如果apk文件存在，则先删除
        if os.path.exists(apk_name):
            os.remove(apk_name)
        logging.info("Find %s(%s), downloading..." % (apk_name, folder_name))
        try:
            cmd = "wget '%s' %s" % (apk_url, saved_path)
            proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            proc.communicate()
            shutil.move(apk_name, file_path)
        except Exception as e:
            logging.warning(e)
            continue
        logging.info("%s has been downloaded to %s" % (apk_name, file_path))
        return file_path
    return None


def get_apk(prj_ver, prj_info):
    data = get_latest_folder(prj_info)
    if data is None:
        logging.warning("Cannot get path info")
        return None
    status, apk_list = get_latest_apk(data, prj_info)
    if status:
        file_path = download_apk(apk_list, prj_ver, prj_info)
        return file_path
    else:
        logging.warning("Cannot get any apk file!")
        return None
