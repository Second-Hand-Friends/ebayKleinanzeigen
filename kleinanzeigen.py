#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111

"""
Created on Tue Oct  6 00:15:14 2015
Updated and improved by x86dev Dec 2017.

@author: Leo; Eduardo; x86dev
"""
import json
import getopt
import os
import signal
import sys
import time
import urllib.parse
from random import randint
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
import logging
from datetime import datetime
from selenium.webdriver.support.ui import Select

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler('kleinanzeigen.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(message)s')

log.addHandler(ch)
log.addHandler(fh)


def profile_read(profile, config):
    if os.path.isfile(profile):
        with open(profile, encoding="utf-8") as file:
            config.update(json.load(file))


def profile_write(profile, config):
    with open(profile, "w+", encoding='utf8') as fh_config:
        text = json.dumps(config, sort_keys=True, indent=4, ensure_ascii=False)
        fh_config.write(text)


def login(config):
    input_email = config['glob_username']
    input_pw = config['glob_password']
    log.info("Login with account email: " + input_email)
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')

    WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.ID, 'gdpr-banner-accept'))).click()

    text_area = WebDriverWait(driver, 1)\
        .until(EC.presence_of_element_located((By.ID, 'login-email')))
    text_area.send_keys(input_email)
    fake_wait(200)

    text_area = driver.find_element_by_id('login-password')
    text_area.send_keys(input_pw)
    fake_wait(200)

    submit_button = driver.find_element_by_id('login-submit')
    submit_button.click()


def fake_wait(ms_sleep=None):
    if ms_sleep is None:
        ms_sleep = randint(600, 2000)
    if ms_sleep < 100:
        ms_sleep = 100
    log.debug("Waiting %d ms ..." % ms_sleep)
    time.sleep(ms_sleep / 1000)


def delete_ad(driver, ad):
    log.info("\tDeleting ad ...")

    driver.get("https://www.ebay-kleinanzeigen.de/m-meine-anzeigen.html")
    fake_wait()

    ad_id_elem = None

    if "id" in ad:
        try:
            ad_id_elem = driver.find_element_by_xpath("//a[@data-adid='%s']" % ad["id"])
        except NoSuchElementException as e:
            log.info("\tNot found by ID")

    if ad_id_elem is None:
        try:
            ad_id_elem = driver.find_element_by_xpath("//a[contains(text(), '%s')]/../../../../.." % ad["title"])
        except NoSuchElementException as e:
            log.info("\tNot found by title")

    if ad_id_elem is not None:
        try:
            btn_del = ad_id_elem.find_element_by_class_name("managead-listitem-action-delete")
            btn_del.click()

            fake_wait()

            btn_confirm_del = driver.find_element_by_id("modal-bulk-delete-ad-sbmt")
            btn_confirm_del.click()

            log.info("\tAd deleted")
            fake_wait(randint(2000, 3000))
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            return True

        except NoSuchElementException as e:
            log.info("\tDelete button not found")
    else:
        log.info("\tAd does not exist (anymore)")

    ad.pop("id", None)
    return False


# From: https://stackoverflow.com/questions/983354/how-do-i-make-python-to-wait-for-a-pressed-key
def wait_key():
    """ Wait for a key press on the console and return it. """
    result = None
    if os.name == 'nt':
        result = input("Press Enter to continue...")
    else:
        import termios
        fd = sys.stdin.fileno()

        oldterm = termios.tcgetattr(fd)
        newattr = termios.tcgetattr(fd)
        newattr[3] = newattr[3] & ~termios.ICANON & ~termios.ECHO
        termios.tcsetattr(fd, termios.TCSANOW, newattr)

        try:
            result = sys.stdin.read(1)
        except IOError:
            pass
        finally:
            termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)

    return result


def post_ad_has_captcha(driver):
    has_captcha = False

    try:
        captcha_field = driver.find_element_by_xpath('//*[@id="postAd-recaptcha"]')
        if captcha_field:
            has_captcha = True
    except NoSuchElementException:
        pass

    log.info(f"Captcha: {has_captcha}")

    return has_captcha


def post_ad_is_allowed(driver):
    is_allowed = True

    # Try checking for the monthly limit per account first.
    try:
        shopping_cart = driver.find_elements_by_xpath('/html/body/div[1]/form/fieldset[6]/div[1]/header')
        if shopping_cart:
            log.info("\t*** Monthly limit of free ads per account reached! Skipping ... ***")
            is_allowed = False
    except:
        pass

    log.info(f"Ad posting allowed: {is_allowed}")

    return is_allowed


def post_ad(driver, ad, interactive):
    log.info("\tPublishing ad '...")

    if config['glob_phone_number'] is None:
        config['glob_phone_number'] = ''

    if ad["price_type"] not in ['FIXED', 'NEGOTIABLE', 'GIVE_AWAY']:
        ad["price_type"] = 'NEGOTIABLE'

    # Navigate to page
    driver.get(ad["caturl"])
    fake_wait(randint(2000, 3500))

    # Select category
    submit_button = driver.find_element_by_css_selector("#postad-step1-sbmt button")

    submit_button.click()
    fake_wait(randint(1000, 3000))

    # Check if posting an ad is allowed / possible
    fRc = post_ad_is_allowed(driver)
    if fRc is False:
        return fRc

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

    if (ad['shipping_type']) != 'NONE':
        try:
            select_element = driver.find_element_by_css_selector('select[id$=".versand_s"]')
            shippment_select = Select(select_element)
            log.debug("\t shipping select found with id: %s" % select_element.get_attribute('id'))
            if (ad['shipping_type']) == 'PICKUP':
                shippment_select.select_by_visible_text("Nur Abholung")
            if (ad['shipping_type']) == 'SHIPPING':
                shippment_select.select_by_visible_text("Versand möglich")
            fake_wait()
        except NoSuchElementException:
            pass

    text_area = driver.find_element_by_id('pstad-price')
    if ad["price_type"] != 'GIVE_AWAY':
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

    # Upload images from photofiles
    if "photofiles" in ad:
        try:
            fileup = driver.find_element_by_xpath("//input[@type='file']")
            for path in ad["photofiles"]:
                path_abs = config["glob_photo_path"] + path
                uploaded_count = len(driver.find_elements_by_class_name("imagebox-thumbnail"))
                log.debug("\tUploading image: %s" % path_abs)
                fileup.send_keys(os.path.abspath(path_abs))
                total_upload_time = 0
                while uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")) and \
                        total_upload_time < 30:
                    fake_wait(500)
                    total_upload_time += 0.5

                if uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")):
                    log.warning("\Could not upload image: %s within %s seconds" % (path_abs, total_upload_time))
                else:
                    log.debug("\tUploaded file in %s seconds" % total_upload_time)
        except NoSuchElementException:
            pass

    # Upload images from directory
    if "photo_dir" in ad:
        try:
            fileup = driver.find_element_by_xpath("//input[@type='file']")
            path = ad["photo_dir"]
            path_abs = config["glob_photo_path"] + path
            if not path_abs.endswith("/"):
                path_abs += "/"
            for filename in os.listdir(path_abs):
                if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    continue
                file_path_abs = path_abs + filename
                uploaded_count = len(driver.find_elements_by_class_name("imagebox-thumbnail"))
                log.debug("\tUploading image: %s" % file_path_abs)
                fileup.send_keys(os.path.abspath(file_path_abs))
                total_upload_time = 0
                while uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")) and \
                        total_upload_time < 30:
                    fake_wait(500)
                    total_upload_time += 0.5
                
                if uploaded_count == len(driver.find_elements_by_class_name("imagebox-thumbnail")):
                    log.warning("\Could not upload image: %s within %s seconds" % (file_path_abs, total_upload_time))
                else:
                    log.debug("\tUploaded file in %s seconds" % total_upload_time)
        except NoSuchElementException:
            pass

    fake_wait()

    submit_button = driver.find_element_by_id('pstad-frmprview')
    if submit_button:
        submit_button.click()

    fake_wait()

    has_captcha = post_ad_has_captcha(driver)
    if has_captcha:
        if interactive:
            log.info("\t*** Manual captcha input needed! ***")
            log.info("\tFill out captcha and submit, after that press Enter here to continue ...")
            wait_key()
        else:
            log.info("\tCaptcha input needed, but running in non-interactive mode! Skipping ...")
            fRc = False

    if fRc:
        try:
            submit_button = driver.find_element_by_id('prview-btn-post')
            if submit_button:
                submit_button.click()
        except NoSuchElementException:
            pass

        try:
            parsed_q = urllib.parse.parse_qs(urllib.parse.urlparse(driver.current_url).query)
            add_id = parsed_q.get('adId', None)[0]
            log.info(f"\tPosted as: {driver.current_url}")
            if "id" not in ad:
                log.info(f"\tNew ad ID: {add_id}")
                ad["date_published"] = datetime.utcnow().isoformat()

            ad["id"] = add_id
            ad["date_updated"] = datetime.utcnow().isoformat()
        except:
            pass

    if fRc is False:
        log.info("\tError publishing ad")

    return fRc


def session_create(config):
    log.info("Creating session")

    options = Options()
    if config.get('headless', False) is True:
        log.info("Headless mode")
        options.add_argument("--headless")
    driver = webdriver.Firefox(firefox_options=options)

    log.info("New session is: %s %s" % (driver.session_id, driver.command_executor._url))

    config['session_id'] = driver.session_id
    config['session_url'] = driver.command_executor._url

    return driver


def session_attach(config):
    log.info("Trying to attach to session %s %s" % (config['session_id'], config['session_url']))

    # Save the original function, so we can revert our patch
    org_command_execute = webdriver.Remote.execute

    def new_command_execute(self, command, params=None):
        if command == "newSession":
            # Mock the response
            return {'success': 0, 'value': None, 'sessionId': config['session_id']}
        else:
            return org_command_execute(self, command, params)

    # Patch the function before creating the driver object
    webdriver.Remote.execute = new_command_execute

    driver = webdriver.Remote(command_executor=config['session_url'], desired_capabilities={})
    driver.session_id = config['session_id']

    try:
        log.info("Current URL is: %s" % driver.current_url)
    except:
        log.info("Session does not exist anymore")
        config['session_id'] = None
        config['session_url'] = None
        driver = None

        # Make sure to put the original executor back in charge.
        webdriver.Remote.execute = org_command_execute

    return driver


def signal_handler(sig, frame):
    print('Exiting script')
    sys.exit(0)


if __name__ == '__main__':

    signal.signal(signal.SIGINT, signal_handler)

    try:
        aOpts, aArgs = getopt.gnu_getopt(sys.argv[1:], "ph", ["profile=", "help"])
    except getopt.error as msg:
        print(msg)
        print("For help use --help")
        sys.exit(2)

    sProfile = ""

    for o, a in aOpts:
        if o in "--profile":
            sProfile = a

    if not sProfile:
        print("No profile specified")
        sys.exit(2)

    log.info('Script started')
    log.info("Using profile: %s" % sProfile)

    config = {}

    profile_read(sProfile, config)

    if config.get('headless') is None:
        config['headless'] = False

    fForceUpdate = False
    fDoLogin = True

    dtNow = datetime.utcnow()

    driver = None

    if config.get('session_id') is not None:
        driver = session_attach(config)

    if driver is None:
        driver = session_create(config)
        profile_write(sProfile, config)
        login(config)
        fake_wait(randint(1000, 4000))

    for ad in config["ads"]:

        fNeedsUpdate = False

        log.info("Handling '%s'" % ad["title"])

        if "date_updated" in ad:
            dtLastUpdated = datetime.fromisoformat(ad["date_updated"])
        else:
            dtLastUpdated = dtNow
        dtDiff = dtNow - dtLastUpdated

        if "enabled" in ad \
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

        if fNeedsUpdate or fForceUpdate:

            delete_ad(driver, ad)

            fPosted = post_ad(driver, ad, True)
            if not fPosted:
                break

            log.info("Waiting for handling next ad ...")
            fake_wait(randint(2000, 6000))

        profile_write(sProfile, config)

    driver.close()
    log.info("Script done")
