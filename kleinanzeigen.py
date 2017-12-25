# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111

"""
Created on Tue Oct  6 00:15:14 2015

@author: Leo; Eduardo
"""
import json
import os
import time
import urlparse
from random import randint
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
    input_email = config['glob_username']
    input_pw = config['glob_password']
    log.info("Login with account email: " + input_email)
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
    fake_wait()
    
    text_area = driver.find_element_by_id('login-email')
    text_area.send_keys(input_email)
    fake_wait()

    text_area = driver.find_element_by_id('login-password')
    text_area.send_keys(input_pw)
    fake_wait()

    submit_button = driver.find_element_by_id('login-submit')
    submit_button.click()


def delete_ad(ad_id):
    driver.get('https://www.ebay-kleinanzeigen.de/m-anzeigen-loeschen.json?ids=%s&pageNum=1' % ad_id)

def fake_wait():
    num_secs = randint(3, 13)
    log.debug("Waiting %d seconds ..." % num_secs)
    time.sleep(num_secs)

def post_ad(ad):
    global log

    if config['glob_phone_number'] is None:
        config['glob_phone_number'] = ''

    if ad["price_type"] not in ['FIXED', 'NEGOTIABLE', 'GIVE_AWAY']:
        ad["price_type"] = 'NEGOTIABLE'

    # Navigate to page
    driver.get(ad["caturl"])
    log.debug("Navigating to category selection page.")
    fake_wait()

    # Select category
    submit_button = driver.find_element_by_css_selector("#postad-step1-sbmt button")
    submit_button.click()

    fake_wait()

    # Fill form
    text_area = driver.find_element_by_id('postad-title')
    text_area.send_keys(ad["title"])
    fake_wait()

    text_area = driver.find_element_by_id('pstad-descrptn')
    desc = config['glob_ad_prefix'] + ad["desc"] + config['glob_ad_suffix']
    desc_list = [x.strip('\\n') for x in desc.split('\\n')]
    for p in desc_list:
        text_area.send_keys(p)
        text_area.send_keys(Keys.RETURN)

    fake_wait()

    text_area = driver.find_element_by_id('pstad-price')
    text_area.send_keys(ad["price"])
    price = driver.find_element_by_xpath("//input[@name='priceType' and @value='%s']" % ad["price_type"])
    price.click()
    fake_wait()

    text_area = driver.find_element_by_id('pstad-zip')
    text_area.clear()
    text_area.send_keys(config["glob_zip"])
    fake_wait()

    if config["glob_phone_number"]:
        text_area = driver.find_element_by_id('postad-phonenumber')
        text_area.clear()
        text_area.send_keys(config["glob_phone_number"])
        fake_wait()

    text_area = driver.find_element_by_id('postad-contactname')
    text_area.clear()
    text_area.send_keys(config["glob_contact_name"])
    fake_wait()

    if config["glob_street"]:
        text_area = driver.find_element_by_id('pstad-street')
        text_area.clear()
        text_area.send_keys(config["glob_street"])
        fake_wait()

    # Upload images
    fileup = driver.find_element_by_xpath("//input[@type='file']")

    for path in ad["photofiles"]:
        path = config["glob_photo_path"] + path
        uploaded_count = len(driver.find_elements_by_class_name("imagebox-thumbnail"))
        fileup.send_keys(os.path.abspath(path))
        total_upload_time = 0
        while uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")) and \
                        total_upload_time < 30:
            fake_wait()
            total_upload_time += 0.5

        log.debug("Uploaded file in %s seconds." % total_upload_time)

    fake_wait()

    submit_button = driver.find_element_by_id('pstad-frmprview')
    submit_button.click()

    submit_button = driver.find_element_by_id('prview-btn-post')
    submit_button.click()

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
    fake_wait()

    for ad in config['ads']:
        log.info('Posting ad titled "%s".' % ad['title'])
        post_ad(ad)

    driver.close()
    currentdatetime = datetime.strptime(datetime.now().strftime("%d %b %Y, %H:%M:%S"), ("%d %b %Y, %H:%M:%S"))
    log.info('Script done at %s' % currentdatetime)
