# -*- coding: utf-8 -*-
"""
Created on Tue Oct  6 00:15:14 2015

@author: Leo; Eduardo
"""
import json
import os
import time
import urlparse
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import logging
from datetime import datetime

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('kleinanzeigen.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(message)s')

log.addHandler(ch)
log.addHandler(fh)

log.info('Kleinanzeigen script started.')
log.debug('\n')

config = {}
driver = webdriver.Firefox()
driver.implicitly_wait(10)


def init_config():
    config_file = "config.json"
    if os.path.isfile(config_file):
        with open(config_file) as data:
            config.update(json.load(data))


def login():
    global driver
    input_email = config['username']
    input_pw = config['password']
    log.info("Login with account email: " + input_email)
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
    text_area = driver.find_element_by_id('login-email')
    text_area.send_keys(input_email)
    text_area = driver.find_element_by_id('login-password')
    text_area.send_keys(input_pw)
    submit_button = driver.find_element_by_id('login-submit')
    submit_button.click()


def delete_ad(ad_id):
    driver.get('https://www.ebay-kleinanzeigen.de/m-anzeigen-loeschen.json?ids=%s&pageNum=1' % ad_id)


def post_ad(
        postad_title,
        pstad_descrptn,
        pstad_price,
        pstad_street,
        pstad_zip,
        postad_contactname,
        caturl,
        photofiles,
        pstad_phone=None,
        price_type=None
):
    global log

    if pstad_phone is None:
        pstad_phone = ''

    if price_type not in ['FIXED', 'NEGOTIABLE', 'GIVE_AWAY']:
        price_type = 'FIXED'

    # Navigate to page
    driver.get(caturl)
    log.debug("Navigating to category selection page.")
    time.sleep(1)

    # Select category
    submit_button = driver.find_element_by_css_selector("#postad-step1-sbmt button")
    submit_button.click()

    # Fill form
    text_area = driver.find_element_by_id('postad-title')
    text_area.send_keys(postad_title)
    text_area = driver.find_element_by_id('pstad-descrptn')
    pstad_descrptnlist = [x.strip('\\n') for x in pstad_descrptn.split('\\n')]
    for p in pstad_descrptnlist:
        text_area.send_keys(p)
        text_area.send_keys(Keys.RETURN)

    text_area = driver.find_element_by_id('pstad-price')
    text_area.send_keys(pstad_price)
    price = driver.find_element_by_xpath("//input[@name='priceType' and @value='%s']" % price_type)
    price.click()
    text_area = driver.find_element_by_id('pstad-zip')
    text_area.clear()
    text_area.send_keys(pstad_zip)
    text_area = driver.find_element_by_id('postad-phonenumber')
    text_area.clear()
    text_area.send_keys(pstad_phone)
    text_area = driver.find_element_by_id('postad-contactname')
    text_area.clear()
    text_area.send_keys(postad_contactname)
    text_area = driver.find_element_by_id('pstad-street')
    text_area.clear()
    text_area.send_keys(pstad_street)

    # Upload images
    fileup = driver.find_element_by_xpath("//input[@type='file']")

    for path in photofiles:
        uploaded_count = len(driver.find_elements_by_class_name("imagebox-thumbnail"))
        fileup.send_keys(os.path.abspath(path))
        total_upload_time = 0
        while uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")) and \
                        total_upload_time < 30:
            time.sleep(0.5)
            total_upload_time += 0.5

        log.debug("Uploaded file in %s seconds." % total_upload_time)

    submit_button = driver.find_element_by_id('pstad-frmprview')
    submit_button.click()
    time.sleep(2)

    submit_button = driver.find_element_by_id('prview-btn-post')
    submit_button.click()
    time.sleep(2)
    log.info("Posted as: %s" % driver.current_url)
    parsed_q = urlparse.parse_qs(urlparse.urlparse(driver.current_url).query)
    ad_id = parsed_q.get('adId', None)[0]
    if ad_id:
        log.info("New ad id: %s." % ad_id)
    else:
        log.info("Error posting/retrieving new id.")

    return ad_id


if __name__ == '__main__':
    log.info("Script for ebay Kleinanzeigen started")
    currentdatetime = datetime.strptime(datetime.now().strftime("%d %b %Y, %H:%M:%S"), ("%d %b %Y, %H:%M:%S"))
    log.info("Script started at %s" % currentdatetime)

    init_config()
    login()
    for ad in config['ads']:
        log.info('Posting ad titled "%s".' % ad['postad_title'])
        post_ad(
            pstad_street=config["street"],
            pstad_zip=config["zip"],
            pstad_phone=config["phone_number"],
            postad_contactname=config["contact_name"],
            **ad)

    driver.close()
    currentdatetime = datetime.strptime(datetime.now().strftime("%d %b %Y, %H:%M:%S"), ("%d %b %Y, %H:%M:%S"))
    log.info('Script done at %s' % currentdatetime)
