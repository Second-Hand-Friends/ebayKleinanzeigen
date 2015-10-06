# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 00:15:14 2015

@author: Leo
"""
import time
import sys, os
from selenium import webdriver 


input_email = 'loppo22@gmail.com'
input_pw = ''
# input_email = input("Enter Email: ")
print ("You entered " + input_email )
# input_pw = input("Enter Password: ")


postad_title = 'Test'
pstad_descrptn = 'TEST'
pstad_price = '10'
pstad_street = 'tests'

driver = webdriver.Firefox()

driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
text_area = driver.find_element_by_id('login-email')
text_area.send_keys(input_email)
text_area = driver.find_element_by_id('login-password')
text_area.send_keys(input_pw )

submit_button = driver.find_element_by_id('login-submit')
submit_button.click()




driver.get('https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben.html#?path=161/225/mainboards&isParent=false')

submit_button = driver.find_element_by_class_name('button')
submit_button.click()
text_area = driver.find_element_by_id('postad-title')
text_area.send_keys(postad_title)
text_area = driver.find_element_by_id('pstad-descrptn')
text_area.send_keys(postad_title)
text_area = driver.find_element_by_id('pstad-price')
text_area.send_keys(pstad_price)
price = driver.find_elements_by_xpath("//input[@name='priceType' and @id='priceType2']")[0]
price.click()
text_area = driver.find_element_by_id('pstad-zip')
text_area.send_keys('70174')
text_area = driver.find_element_by_id('postad-contactname')
text_area.send_keys('TEST1')
text_area = driver.find_element_by_id('pstad-street')
text_area.send_keys('pstad_street')

driver.find_element_by_xpath("//input[@type='file']").send_keys(r'C:\Users\Leo\Desktop\ebay Kleinanzeigen\pic.png')



time.sleep(5)

driver.close()
