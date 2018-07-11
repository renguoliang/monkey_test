#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class Keyboard():
    def __init__(self, appium_driver):
        self.appium_driver = appium_driver

    def login(self):
        self.appium_driver.launch_app()
        print "launch_app()"
        time.sleep(15)
        # 点击switch
        self.appium_driver.action.tap(x=550, y=1525).perform()
        time.sleep(5)
        self.appium_driver.back()

        el = self.appium_driver.wait_element_by_android_uiautomator('new UiSelector().text(" Cheetah Keyboard ❤ ❤ ❤ ")')
        self.appium_driver.tap(el)

        self.appium_driver.run_wathcer()

        self.appium_driver.action.tap(x=550, y=1525).perform()
        el = self.appium_driver.wait_element_by_android_uiautomator('new UiSelector().text(" Cheetah Keyboard ❤ ❤ ❤ ")')
        self.appium_driver.tap(el)
        time.sleep(3)

        self.appium_driver.run_wathcer()
        time.sleep(3)
        self.appium_driver.back()
        self.appium_driver.back()
        self.appium_driver.back()

        time.sleep(3)


