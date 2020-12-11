#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111
from selenium import webdriver

driver = webdriver.Firefox()
driver.get("https://www.wikipedia.org")

try:
    elem = driver.find_elements_by_xpath('/html/body/div[6]/div[3]/div[8]/a/div[2]/span[1]')
    if elem:
        print("Found")
    else:
        print("Not found")
except:
    pass

driver.close()
