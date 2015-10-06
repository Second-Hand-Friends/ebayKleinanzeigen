# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 00:15:14 2015

@author: Leo
"""
import time, csv, os
from selenium import webdriver 
from path import Path
       
        

def login():
    global driver
    input_email = 'loppo22@gmail.com'
    input_pw = ''
    # input_email = input("Enter Email: ")
    print ("You entered " + input_email )
    # input_pw = input("Enter Password: ")
    driver = webdriver.Firefox()
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
    text_area = driver.find_element_by_id('login-email')
    text_area.send_keys(input_email)
    text_area = driver.find_element_by_id('login-password')
    text_area.send_keys(input_pw )
    submit_button = driver.find_element_by_id('login-submit')
    submit_button.click()

def open_cat( cat ):
    # Kategorie öffnen
    if cat == "Mainboard": ## usw.
        print ("cat Mainboard")
  
with open('data.csv') as csvfile:
    global postad_title, pstad_descrptn, pstad_price, pstad_street, pstad_zip, postad_contactname, price, file1, file2
    spamreader = csv.DictReader(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
    for row in spamreader: 
        print(row['postad_title'], row['pstad_descrptn'], row['pstad_price'], row['pstad_street'], row['pstad_zip'] , row['postad_contactname'], row['price'])
        postad_title, pstad_descrptn, pstad_price, pstad_street, pstad_zip, postad_contactname, price   = row['postad_title'], row['pstad_descrptn'], row['pstad_price'], row['pstad_street'], row['pstad_zip'] , row['postad_contactname'], row['price']
        file1 = row["file1"]
        file2 = row["file2"]

login()

driver.get('https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben.html#?path=161/225/mainboards&isParent=false')

submit_button = driver.find_element_by_class_name('button')
submit_button.click()
text_area = driver.find_element_by_id('postad-title')
text_area.send_keys(postad_title)
text_area = driver.find_element_by_id('pstad-descrptn')
text_area.send_keys(postad_title)
text_area = driver.find_element_by_id('pstad-price')
text_area.send_keys(pstad_price)
price = driver.find_elements_by_xpath("//input[@name='priceType' and @id='%s']"% price)[0]
price.click()
text_area = driver.find_element_by_id('pstad-zip')
text_area.send_keys(pstad_zip)
text_area = driver.find_element_by_id('postad-contactname')
text_area.send_keys(postad_contactname)
text_area = driver.find_element_by_id('pstad-street')
text_area.send_keys(pstad_street)
driver.find_element_by_xpath("//input[@type='file']").send_keys("{} {}".format(file1, file2))

# driver.find_element_by_xpath("//input[@type='file']").send_keys(file2)
submit_button = driver.find_element_by_id('pstad-frmprview')
submit_button.click()

#  # Vorschau 
# veröffentlichen pstad-submit
time.sleep(5)

driver.close()
