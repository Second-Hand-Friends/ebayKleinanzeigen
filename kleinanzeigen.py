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
import dateutil.parser

json.JSONEncoder.default = \
    lambda self, obj: \
        (obj.isoformat() if isinstance(obj, datetime) else None)

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('kleinanzeigen.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(message)s')

log.addHandler(ch)
log.addHandler(fh)

log.info('Script started')
log.debug('\n')

config = {}
driver = webdriver.Firefox()
driver.implicitly_wait(10)

def read_config():
    fhConfig = "config.json"
    if os.path.isfile(fhConfig):
        with open(fhConfig) as data:
            config.update(json.load(data))

def write_config():
    fhConfig = open("config.json", "w+")
    fhConfig.write(json.dumps(config, sort_keys=True, indent=4))
    fhConfig.close()

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

def delete_ad(ad):
    driver.get("https://www.ebay-kleinanzeigen.de/m-meine-anzeigen.html")
    fake_wait()
    btn_del = driver.find_element_by_xpath("//a[@data-adid='%s' and @data-gaevent='MyAds,DeleteAdBegin']" % ad["id"])    
    if btn_del:
        btn_del.click()
        fake_wait()
        btn_confirm_del = driver.find_element_by_id("modal-bulk-delete-ad-sbmt")
        if btn_confirm_del:
            btn_confirm_del.click()

def fake_wait(msSleep=None):
    if msSleep is None:
        msSleep = randint(700, 3333)
    log.debug("Waiting %d ms ..." % msSleep)
    time.sleep(msSleep / 1000)

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
    ad["id"] = parsed_q.get('adId', None)[0]
    if "id" in ad:
        log.info("New ad ID: %s" % ad["id"])
    else:
        log.info("Error posting/retrieving new ID")

    ad["date_updated"] = datetime.utcnow()

    return


if __name__ == '__main__':
    log.info("Script started")

    read_config()

    fForceUpdate = False
    fDoLogin     = True

    dtNow = datetime.utcnow()

    for ad in config["ads"]:
        
        fNeedsUpdate = False
        fPublished   = False
        
        log.info("Handling '%s'" % ad["title"])

        if "date_updated" in ad:
            dtLastUpdated = dateutil.parser.parse(ad["date_updated"])
        else:
            dtLastUpdated = dtNow
        dtDiff            = dtNow - dtLastUpdated      

        if ad["enabled"] == "1":
            if "id" in ad:
                log.info("\tAlready published (%d days ago)" % dtDiff.days)
                fPublished = True
                if dtDiff.days > 4:
                    fNeedsUpdate = True
            else:
                log.info("\tNot published yet")
                fNeedsUpdate = True
        else:
            log.info("\tDisabled, skipping")

        if fNeedsUpdate \
        or fForceUpdate:

            if fDoLogin:
                login()
                fake_wait()
                fDoLogin = False

            if fPublished:
                log.info("\tDeleting existing ad (%s)" % ad["id"])
                delete_ad(ad)
                fake_wait()
            else:
                ad["date_posted"] = datetime.utcnow()

            log.info("\tPublishing ad ...")
            post_ad(ad)

            time.sleep(15 * 1000)

    write_config()

    driver.close()
    log.info("Script done")
