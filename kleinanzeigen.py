# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111

"""
Created on Tue Oct  6 00:15:14 2015
Updated and improved by x86dev Dec 2017.

@author: Leo; Eduardo; x86dev
"""
import json
import os
import time
import urlparse
from random import randint
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
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

def fake_wait(msSleep=None):
    if msSleep is None:
        msSleep = randint(777, 3333)
    if msSleep < 100:
        msSleep = 100
    log.debug("Waiting %d ms ..." % msSleep)
    time.sleep(msSleep / 1000)

def delete_ad(ad):
    global log

    log.info("\tDeleting ad ...")

    driver.get("https://www.ebay-kleinanzeigen.de/m-meine-anzeigen.html")
    fake_wait()

    fFound = False

    if "id" in ad:
        log.info("\tSearching by ID")
        try:
            btn_del = driver.find_element_by_xpath("//a[@data-adid='%s' and @data-gaevent='MyAds,DeleteAdBegin']" % ad["id"])
            btn_del.click()

            fake_wait()

            fFound = True

        except NoSuchElementException as e:
            print str(e)

    if not fFound:
        log.info("\tSearching by title")
        try:
            adIdElem = driver.find_element_by_xpath("//a[contains(text(), '%s')]/../../../../.." % ad["title"])
            adId     = adIdElem.get_attribute("data-adid")
            if adId is not None:
                log.info("\tAd ID is now %s" % adId)

                btn_del = driver.find_element_by_xpath("//a[@data-adid='%s' and @data-gaevent='MyAds,DeleteAdBegin']" % adId)
                btn_del.click()

                fake_wait()

                fFound = True

        except NoSuchElementException as e:
            pass

    if fFound:

        fake_wait()

        try:
            btn_confirm_del = driver.find_element_by_id("modal-bulk-delete-ad-sbmt")
            btn_confirm_del.click()

            log.info("\tAd deleted")

        except NoSuchElementException as e:
            print str(e)
    else:
        log.info("\tAd does not exist (anymore)")

    ad.pop("id", None)

def post_ad(ad, fInteractive):
    global log

    fRc = True

    log.info("\tPublishing ad '...")

    if config['glob_phone_number'] is None:
        config['glob_phone_number'] = ''

    if ad["price_type"] not in ['FIXED', 'NEGOTIABLE', 'GIVE_AWAY']:
        ad["price_type"] = 'NEGOTIABLE'

    # Navigate to page
    driver.get(ad["caturl"])
    fake_wait(randint(4000, 8000))

    # Select category
    submit_button = driver.find_element_by_css_selector("#postad-step1-sbmt button")
    submit_button.click()
    fake_wait(randint(4000, 8000))

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

        log.debug("\tUploaded file in %s seconds." % total_upload_time)

    fake_wait()

    submit_button = driver.find_element_by_id('pstad-frmprview')
    if submit_button:
        submit_button.click()

    fake_wait()

    try:
        submit_button = driver.find_element_by_id('prview-btn-post')
        if submit_button:
            submit_button.click()
    except NoSuchElementException:
        pass

    try:
        captcha_field = driver.find_element_by_id('recaptcha_response_field')
        if captcha_field:
            if fInteractive:            
                log.info("\t*** Manual captcha input needed! ***")
                raw_input("\tFill out captcha and submit, after that press Enter here to continue ...")
            else:
                log.info("\tCaptcha input needed, but running in non-interactive mode! Skipping ...")
    except NoSuchElementException:
        pass

    try:
        parsed_q = urlparse.parse_qs(urlparse.urlparse(driver.current_url).query)
        addId = parsed_q.get('adId', None)[0]
        log.info("\tPosted as: %s" % driver.current_url)
        if "id" not in ad:
            log.info("\tNew ad ID: %s" % addId)
            ad["date_published"] = datetime.utcnow()

        ad["id"]           = addId
        ad["date_updated"] = datetime.utcnow()
    except:
        pass

    try:
        shopping_cart = driver.find_element_by_id('myftr-shppngcrt-frm')
        if shopping_cart:
            log.info("\t*** Monthly limit of free ads per account reached! Skipping ... ***")
            fRc = False
    except:
        pass

    if fRc is False:
        log.info("\tError publishing ad")

    return fRc


if __name__ == '__main__':
    log.info("Script started")

    read_config()

    fForceUpdate = False
    fDoLogin     = True

    dtNow = datetime.utcnow()

    for ad in config["ads"]:

        fNeedsUpdate = False

        log.info("Handling '%s'" % ad["title"])

        if "date_updated" in ad:
            dtLastUpdated = dateutil.parser.parse(ad["date_updated"])
        else:
            dtLastUpdated = dtNow
        dtDiff            = dtNow - dtLastUpdated

        if  "enabled" in ad \
        and ad["enabled"] == "1":
            if "date_published" in ad:
                log.info("\tAlready published (%d days ago)" % dtDiff.days)
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
            else:
                log.info("Waiting for handling next ad ...")
                time.sleep(15)

            delete_ad(ad)
            fake_wait()

            fPosted = post_ad(ad, True)
            if not fPosted:
                break

        write_config()

    driver.close()
    log.info("Script done")
