#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class Launcher():
    def __init__(self, appium_driver):
        self.appium_driver = appium_driver

    def login(self):
        self.appium_driver.launch_app()
        time.sleep(8)
        self.appium_driver.force_stop()
        time.sleep(3)
        self.appium_driver.launch_app()
        time.sleep(8)
        self.appium_driver.back()
        time.sleep(5)
        self.appium_driver.run_wathcer()
        time.sleep(5)
        self.appium_driver.back()

    def force_stop(self):
        self.appium_driver.force_stop()
        time.sleep(5)
        self.appium_driver.back()




