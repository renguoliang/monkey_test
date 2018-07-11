#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class TextOne():
    def __init__(self, appium_driver):
        self.appium_driver = appium_driver

    def login(self):
        self.appium_driver.launch_app()
        time.sleep(15)
        el = self.appium_driver.wait_element_by_id("com.cmcm.textone:id/a9h")
        self.appium_driver.tap(el)
        el = self.appium_driver.wait_element_by_id("com.google.android.gms:id/account_name")
        self.appium_driver.tap(el)
        time.sleep(15)
        el = self.appium_driver.run_wathcer()
        time.sleep(3)
        el = self.appium_driver.wait_element_by_id("com.cmcm.textone:id/a9a")
        self.appium_driver.tap(el)





