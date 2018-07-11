#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time

class liveme():
    def __init__(self, appium_driver):
        self.appium_driver = appium_driver

    def login(self):
        self.appium_driver.launch_app()
        time.sleep(15)
        el = self.appium_driver.wait_element_by_id("com.cmcm.live:id/layout_login_fifth")
        self.appium_driver.tap(el)
        el = self.appium_driver.wait_element_by_id("com.cmcm.live:id/id_google_plus")
        self.appium_driver.tap(el)
        el = self.appium_driver.wait_element_by_id("com.google.android.gms:id/account_name")
        self.appium_driver.tap(el)
        el = self.appium_driver.wait_element_by_id("com.cmcm.live:id/check_in_dismiss")
        if el:
            self.appium_driver.tap(el)

        time.sleep(6)
        el = self.appium_driver.run_wathcer()



