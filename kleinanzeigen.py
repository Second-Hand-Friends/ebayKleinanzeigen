# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 00:15:14 2015

@author: Leo
"""
import time, csv
from selenium import webdriver 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait # available since 2.4.0
from selenium.webdriver.support import expected_conditions as EC # available since 2.26.0
import logging
from datetime import datetime

logging.basicConfig(format='%(asctime)s %(message)s', filename='kleinanzeigen.log',level=logging.DEBUG)
logging.info('Kleinanzeigen script gestartet')
logging.debug('\n')


def login():
    global driver
    input_email = 'loppo22@gmail.com'
    input_pw = ''
    # input_email = input("Enter Email: ")
    print ("Login with account email:" + input_email )
    # input_pw = input("Enter Password: ")
    driver = webdriver.Firefox()
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
    text_area = driver.find_element_by_id('login-email')
    text_area.send_keys(input_email)
    text_area = driver.find_element_by_id('login-password')
    text_area.send_keys(input_pw )
    submit_button = driver.find_element_by_id('login-submit')
    submit_button.click()
    
def prase():  
    global pstad_descrptnlist, price,  files, file, filecount, caturl, postad_title, pstad_descrptn, pstad_price, pstad_street, pstad_zip, postad_contactname, price
    logging.info('Einstellen gestartet')   
    with open('data.csv') as csvfile:
        spamreader = csv.DictReader(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for row in spamreader:
            files = []
            print(row['postad_title'], row['pstad_price'], row['pstad_street'], row['pstad_zip'] , row['postad_contactname'], row['price'], row['caturl'], row['filecount'])
            postad_title, pstad_descrptn, pstad_price, pstad_street, pstad_zip, postad_contactname, price, caturl, filecount = row['postad_title'], row['pstad_descrptn'], row['pstad_price'], row['pstad_street'], row['pstad_zip'] , row['postad_contactname'], row['price'], row['caturl'], row['filecount']
            for x in range(1, int(filecount) + int(1)):                
                file = row['file%s'%x]
                files.append(file)
                
            einstellen()

def einstellen():
    global pstad_descrptnlist, price,  files, file, filecount, caturl, postad_title, pstad_descrptn, pstad_price, pstad_street, pstad_zip, postad_contactname, price    
    driver.get(caturl)
    submit_button = driver.find_element_by_class_name('button')
    submit_button.click()
    text_area = driver.find_element_by_id('postad-title')
    text_area.send_keys(postad_title)
    text_area = driver.find_element_by_id('pstad-descrptn')    
    pstad_descrptnlist = [x.strip('\\n') for x in pstad_descrptn.split('\\n')]       
    for p in pstad_descrptnlist:        
        text_area.send_keys(p)
        text_area.send_keys(Keys.RETURN)
    time.sleep(1)
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
    fileup = driver.find_element_by_xpath("//input[@type='file']")
    print (files)
    for path in files:
        time.sleep(4)        
        fileup.send_keys(path)
        # WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.CLASS_NAME, "pictureupload-thumbnails-remove")))            
    time.sleep(5)   
    submit_button = driver.find_element_by_id('pstad-frmprview')
    submit_button.click()
    
    #  # Vorschau 
    # veröffentlichen pstad-submit
    time.sleep(10)
    
def delete():
    print("Lösche alle Anzeigen die nicht noch online sind.")
    
    
    
print ("Script für ebay Kleinanzeigen gestartet")
currentdatetime = datetime.strptime(datetime.now().strftime("%d %b %Y, %H:%M:%S"), ("%d %b %Y, %H:%M:%S"))   
print ("Script gestartet um %s" %currentdatetime)
print ("Füge Produkte ein")
login()
prase()
driver.close()
logging.debug('\n')