#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class CleanMaster():
    def __init__(self, appium_driver):
        self.appium_driver = appium_driver

    def login(self):
        self.appium_driver.launch_app()
        time.sleep(15)
        el = self.appium_driver.wait_element_by_android_uiautomator('new UiSelector().text("START")')
        self.appium_driver.tap(el)
        time.sleep(3)
        el = self.appium_driver.run_wathcer()



