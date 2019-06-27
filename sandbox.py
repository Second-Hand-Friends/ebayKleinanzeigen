#!/usr/bin/python
# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111
import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

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
