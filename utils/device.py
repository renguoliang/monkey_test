#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import time
import re
import random
import logging
import uiautomator2 as u2
import urllib2
import json
import thread

from time import sleep
from utils import timeout_command
# from uiautomator import Device
import subprocess

def req_url(url):
    req = urllib2.urlopen(url)
    page = req.read()
    page_dict = json.loads(page)
    return page_dict

def get_code(id):
    url = "http://i.api.link.lianjia.com/folio/passport/login/code.json?channel=link&userCode={}".format(id)
    req_dict =req_url(url)
    code = req_dict['data']['code']
    return code
def click_premission(d):
    alerts = ['ALLOW', 'SKIP', 'OK', 'NEXT TIME']
    num = 3
    while num > 0:
        for alert in alerts:
            if d(text=alert).exists:
                d(text=alert).click()
        num -= 1

def click_install(d):
    num = 5
    while num >0:
        if d.exists(resourceId="android:id/button1"):
            d(resourceId="android:id/button1").click()
        elif d.exists(resourceId="com.android.packageinstaller:id/decide_to_continue"):
            d(resourceId="com.android.packageinstaller:id/decide_to_continue").click()
        elif d.exists(resourceId="android:id/button1"):
            d(resourceId="android:id/button1").click()
            return
        sleep(5)
        num -= 1

class Devices:
    def __init__(self, sn):
        self.sn = sn
        self.os = ""
        self.screen = ""
        self.model = ""
        self.__set_device_info()

    def __set_device_info(self):
        # 获取本机所有设备名
        rst = timeout_command.run("adb devices")
        sn_list = re.findall(r"(.+?)\s+device\n", rst)
        # 判断device是否存在
        if self.sn not in sn_list:
            logging.error("device [{}] not found".format(self.sn))
            sys.exit(-1)
        # 获取系统版本号
        cmd = "adb -s {} shell getprop ro.build.version.release".format(self.sn)
        rst = timeout_command.run(cmd)
        if rst is None:
            logging.warning("[device_info] time out: {}".format(cmd))
        elif "error" in rst:
            logging.warning("[device_info] cannot execute: {}".format(cmd))
            logging.warning("[device_info] result: {}".format(rst))
        else:
            try:
                os_version = re.findall(r"\d.\d.\d|\d.\d|[A-Z]", rst)[0]
                self.os = os_version
            except Exception as e:
                logging.warning("[device_info] failed to regex os from {}. {}".format(rst, e))
        # 获取分辨率
        cmd = "adb -s {} shell dumpsys window | grep init".format(self.sn)
        rst = timeout_command.run(cmd)
        if rst is None:
            logging.warning("[device_info] time out: {}".format(cmd))
        elif "error" in rst:
            logging.warning("[device_info] cannot execute: {}".format(cmd))
            logging.warning("[device_info] result: {}".format(rst))
        else:
            try:
                screen = re.findall(r"init=(\d{3,4}x\d{3,4})", rst)[0]
                self.screen = screen
            except Exception as e:
                logging.warning("[device_info] failed to regex screen from {}. {}".format(rst, e))
        # 获取设备名
        cmd = "adb -s {} shell getprop ro.product.model".format(self.sn)
        rst = timeout_command.run(cmd)
        if rst is None:
            logging.warning("[device_info] time out: {}".format(cmd))
        elif "error" in rst:
            logging.warning("[device_info] cannot execute: {}".format(cmd))
            logging.warning("[device_info] result: {}".format(rst))
        else:
            try:
                model = rst.strip()
                self.model = model
            except Exception as e:
                logging.warning("[device_info] failed to get model. {}".format(e))



    def install(self, package):
        # 安装包
        cmd = "adb -s {} install -r {}".format(self.sn, package.path)
        d = u2.connect_usb(self.sn)
        thread.start_new_thread(click_install,(d,))
        rst = timeout_command.run(cmd,600)
        if rst is None:
            logging.error("[install] failed to install, the command is: {}".format(cmd))
            sys.exit(-1)
        elif "Success" in rst:
            logging.info("[install] succeeded in installing {}".format(package.name))
        elif "Failure" in rst:
            try:
                key = re.findall(r"Failure \[(.+?)\]", rst)[0]
            except Exception as e:
                logging.debug(e)
                key = "NULL"
            logging.error("[install] failed to install {}, reason: {}".format(package.name, key))
            sys.exit(-1)

    def uninstall(self, package):
        # 卸载包
        cmd = "adb -s {} uninstall {}".format(self.sn, package.name)
        rst = timeout_command.run(cmd, 600)
        if rst is None:
            logging.error("[uninstall] failed to uninstall, the command is: {}".format(cmd))
        elif "Success" in rst:
            logging.info("[uninstall] succeeded in uninstalling {}".format(package.name))
        elif "Failure" in rst:
            try:
                key = re.findall(r"Failure \[(.+?)\]", rst)[0]
            except Exception as e:
                logging.debug(e)
                key = "NULL"
            logging.error("[uninstall] failed to uninstall {}, reason: {}".format(package.name, key))

    def enable_simiasque(self):
        # 启动simiasque
        cmd = "adb -s {} shell am start -n org.thisisafactory.simiasque/org.thisisafactory.simiasque.MyActivity_".format(self.sn)
        timeout_command.run(cmd)
        time.sleep(1)
        # 返回桌面
        cmd = "adb -s {} shell input keyevent KEYCODE_HOME".format(self.sn)
        timeout_command.run(cmd)
        time.sleep(1)
        # 打开simiasque开关
        cmd = "adb -s {} shell am broadcast -a org.thisisafactory.simiasque.SET_OVERLAY --ez enable true".format(self.sn)
        timeout_command.run(cmd)

    def disable_simiasque(self):
        # 关闭simiasque开关
        cmd = "adb -s {} shell am broadcast -a org.thisisafactory.simiasque.SET_OVERLAY --ez enable false".format(self.sn)
        timeout_command.run(cmd)

    def enable_wifi_manager(self):
        # 启动Wifi Manager
        cmd = "adb -s {} shell am start -n com.ntflc.wifimanager/.MainActivity".format(self.sn)
        timeout_command.run(cmd)
        time.sleep(1)
        # 返回桌面
        cmd = "adb -s {} shell input keyevent KEYCODE_HOME".format(self.sn)
        timeout_command.run(cmd)

    def dumpsys_activity(self, path):
        dumpsys_name = "dumpsys_{}.txt".format(self.sn)
        # adb shell dumpsys activity
        cmd = "adb -s {} shell dumpsys activity > {}/{}".format(self.sn, path, dumpsys_name)
        logging.info(cmd)
        timeout_command.run(cmd)

    def turn_off_screen(self):
        cmd = "adb -s {} shell input keyevent POWER".format(self.sn)
        timeout_command.run(cmd)

    def run_monkey(self, package, path, throttle=700, cnt=10000):
        #如果是launcher 启动后30s退出再执行monkey
        if package.name == "com.ksmobile.launcher":
            cmd = "adb -s {} shell am start -n com.ksmobile.launcher/com.ksmobile.launcher.SplashActivity".format(self.sn)
            timeout_command.run(cmd)
            time.sleep(30)
            cmd = "adb -s {} shell am force-stop {}".format(self.sn, package.name)
            os.popen(cmd)

        time.sleep(3)
        # 生成随机数
        rand = random.randint(0, 65535)
        # 执行monkey命令
        cmd = "adb -s {} shell monkey -p {} -s {} --ignore-crashes --ignore-timeouts --throttle {} -v {} > {}".format(
            self.sn, package.name, rand, throttle, cnt, path
        )
        logging.info(cmd)
        os.popen(cmd)
        time.sleep(5)
        # 停止进程
        # cmd = "adb -s {} shell am force-stop {}".format(self.sn, package.name)
        # os.popen(cmd)

    def login_app(self,package):
        try:
            if package.name == "com.homelink.im":
                d = u2.connect_usb(self.sn)
                d.app_start("com.homelink.im")
                d(resourceId="com.lianjia.link.plugin:id/et_username").set_text(package.usr_id)
                d(resourceId="com.lianjia.link.plugin:id/et_password").set_text(package.usr_pwd)
                sleep(2)
                d.press("back")
                d(resourceId="com.lianjia.link.plugin:id/btn_login").click()

                if d.exists(resourceId="com.lianjia.link.plugin:id/et_auth_code"):
                    print "get code"
                    code = get_code(id)
                    d(resourceId="com.lianjia.link.plugin:id/et_auth_code").set_text(code)
                    sleep(2)
                    d.press("back")
                    d(resourceId="com.lianjia.link.plugin:id/btn_login").click()
            # elif package.name == "com.cmcm.shorts":
            #     cmd = "adb -s {} shell am start -n com.cmcm.shorts/com.cmcm.cmlive.activity.SplashActivity".format(self.sn)
            #     timeout_command.run(cmd)
            #     time.sleep(10)
            #     d = Device('{}'.format(self.sn))
            #
            #     click_premission(d)
            #     d(resourceId="com.cmcm.shorts:id/home_bottom_user").click()
            #     d(resourceId="com.cmcm.shorts:id/layout_login_second").click()
            #     click_premission(d)
            #     d(text="Guoliang Ren").click()
            #     click_premission(d)
            #     time.sleep(15)
            #     d.press.home()
            # elif package.name == "com.cmcm.live":
            #     cmd = "adb -s {} shell am start -n com.cmcm.live/com.cmcm.cmlive.activity.SplashActivity".format(self.sn)
            #     timeout_command.run(cmd)
            #     time.sleep(10)
            #     d = Device('{}'.format(self.sn))
            #     click_premission(d)
            #     d(resourceId="com.cmcm.live:id/layout_login_fifth").click()
            #     d(resourceId="com.cmcm.live:id/id_google_plus").click()
            #     click_premission(d)
            #     d(text="Guoliang Ren").click()
            #     time.sleep(10)
            #     click_premission(d)
            #     d.press.home()
            # elif package.name == "com.cmcm.textone":
            #     cmd = "adb -s {} shell am start -n com.cmcm.textone/com.yy.iheima.startup.SplashActivity".format(self.sn)
            #     timeout_command.run(cmd)
            #     time.sleep(15)
            #     d = Device('{}'.format(self.sn))
            #     d(resourceId="com.cmcm.textone:id/googleView").click()
            #     d(text="Guoliang Ren").click()
            #     time.sleep(20)
            #     d.press.home()
            # elif package.name == "panda.keyboard.emoji.theme":
            #     cmd = "adb -s {} shell am start -n panda.keyboard.emoji.theme/cmcm.wizard.SetupActivity".format(self.sn)
            #     timeout_command.run(cmd)
            #     time.sleep(8)
            #     d = Device('{}'.format(self.sn))
            #     d.click(770, 2100)
            #     time.sleep(2)
            #     d.press.back()
            #     time.sleep(2)
            #     d(text=' Cheetah Keyboard ❤ ❤ ❤ ').click()
            #     d(text='OK').click()
            #     d(text='OK').click()
            #     time.sleep(5)
            #     d.click(770, 2100)
            #     d(text=' Cheetah Keyboard ❤ ❤ ❤ ').click()
            #     time.sleep(5)
            #     click_premission(d)
            #     d.press.back()
            #     d.press.back()
            #     d.press.back()
            # else :
            #     logging.info("Don't need login")
        except Exception as e:
            logging.debug(e)
            logging.error("login fail")

    def export_hprof(self,package,prj_info):
        if "activitylist" in prj_info.keys():
            # d = Device('{}'.format(self.sn))
            # d.press.home()
            timeout_command.command("adb -s {} shell input keyevent 3".format(self.sn))
            timeout_command.command("adb -s {} shell dumpsys meminfo {}".format(self.sn,package.name))
            return self.dump_hprof(package, prj_info)


    def dump_hprof(self, package, prj_info):
        timestamp = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
        timeout_command.run("adb -s {} shell am dumpheap {} /data/local/tmp/{}.hprof".format(self.sn, package.name, timestamp))
        if not os.path.exists("hprof/{}".format(package.name)):
            os.makedirs("hprof/{}".format(package.name))
        path = os.getcwd()
        jar_path = "{}/hprof/run/anylize_hprof_rgl.jar".format(path)
        hprof_path = "{}/hprof/{}/".format(path, package.name)
        hprof = hprof_path + "{}.hprof".format(timestamp)
        activelist_path = "{}/hprof/run/".format(path) + prj_info["activitylist"]
        hprof_size = self.pull_hprof(hprof, hprof_path, timestamp)
        retry_num = 0
        #判断下载的hprof文件大于20兆，确保文件完整
        while hprof_size <= 2000000:
            hprof_size = self.pull_hprof(hprof, hprof_path, timestamp)
            retry_num += 1
            time.sleep(5)
            print "当前重试次数", retry_num
            if retry_num == 10:
                break
        timeout_command.run("adb -s {} shell rm /data/local/tmp/{}.hprof".format(self.sn, timestamp))
        if hprof_size > 0:
            timeout_command.run("java -jar {} {} {} {} {}".format(jar_path, hprof, activelist_path, package.name, package.versioncode))
            return "SUCCESS"
        else:
            return "FAILED"

    def pull_hprof(self, hprof, hprof_path, timestamp):
        time.sleep(10)
        timeout_command.subproces("adb -s {} pull /data/local/tmp/{}.hprof {}".format(self.sn, timestamp, hprof_path))
        hprof_size = round(os.path.getsize(hprof))
        return hprof_size