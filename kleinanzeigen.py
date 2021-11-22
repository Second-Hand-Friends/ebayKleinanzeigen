#!/usr/bin/env python
# -*- coding: utf-8 -*-
# pylint: disable=C0301
# pylint: disable=C0111

"""
Created on Tue Oct  6 00:15:14 2015
Updated and improved by x86dev Dec 2017.

@author: Leo; Eduardo; x86dev
"""
import getopt
import json
import logging
import os
import signal
import sys
import time
import urllib.parse
from datetime import datetime
from platform import python_version_tuple
from random import randint

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium_stealth import stealth

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
    
    driver.get('https://www.ebay-kleinanzeigen.de')
              
    # wait for the 'accept cookie' banner to appear
    WebDriverWait(driver, 6).until(EC.element_to_be_clickable((By.ID, 'gdpr-banner-accept'))).click()
    
    fake_wait(2000)   
    
    driver.get('https://www.ebay-kleinanzeigen.de/m-einloggen.html')
    
    fake_wait(2000)
    
    text_area = WebDriverWait(driver, 1).until(EC.presence_of_element_located((By.ID, 'login-email')))
    text_area.send_keys(input_email)
    fake_wait(200)

    has_captcha = login_has_captcha(driver)
    if has_captcha:
        log.info("\t*** Manual captcha input needed! ***")
        log.info("\tFill out captcha but DON'T submit. After that press Enter here to continue ...")
        wait_key()

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
            ad_id_elem = driver.find_element_by_xpath("//li[@data-adid='%s']" % ad["id"])
        except NoSuchElementException:
            log.info("\tNot found by ID")
            try: 
                next_page = driver.find_element_by_class_name("Pagination--next")
                next_page.click()
                fake_wait()
                ad_id_elem = driver.find_element_by_xpath("//li[@data-adid='%s']" % ad["id"])
            except NoSuchElementException:
                log.info("\tNot found by ID on second page")

    if ad_id_elem is None:
        try:
            ad_id_elem = driver.find_element_by_xpath("//article[.//a[contains(text(), '%s')]]" % ad["title"])
        except NoSuchElementException:
            log.info("\tNot found by title")

    if ad_id_elem is not None:
        try:
            btn_del = ad_id_elem.find_element_by_class_name("managead-listitem-action-delete")
            btn_del.click()

            fake_wait()
            
            toogle_delete_reason = driver.find_element_by_id("DeleteWithoutReason")
            toogle_delete_reason.click()
            
            fake_wait()
            
            btn_confirm_del = driver.find_element_by_id("sold-celebration-sbmt")
            btn_confirm_del.click()
            
            log.info("\tAd deleted")
            fake_wait(randint(2000, 3000))
            webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
            return True
        except NoSuchElementException:
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

def login_has_captcha(driver):
    has_captcha = False

    try:
        captcha_field = driver.find_element_by_xpath('//*[@id="login-recaptcha"]')
        if captcha_field:
            has_captcha = True
    except NoSuchElementException:
        pass

    log.info(f"Captcha: {has_captcha}")

    return has_captcha

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
    log.info("\tPublishing ad ...")

    if config['glob_phone_number'] is None:
        config['glob_phone_number'] = ''

    if ad["price_type"] not in ['FIXED', 'NEGOTIABLE', 'GIVE_AWAY']:
        ad["price_type"] = 'NEGOTIABLE'

    # Navigate to page
    driver.get('https://www.ebay-kleinanzeigen.de/p-anzeige-aufgeben.html')
    fake_wait(randint(2000, 3500))

    category_selected = False
    try:
      driver.find_element_by_id('pstad-lnk-chngeCtgry')
      log.info("Using new layout")
    except:
      log.info("Using old layout")
      # legacy handling for old page layout where you have to first select the category (currently old and new layout are served randomly)
      driver.get(ad["caturl"].replace('p-kategorie-aendern', 'p-anzeige-aufgeben'))
      fake_wait(300)
      driver.find_element_by_css_selector("#postad-step1-sbmt button").click()
      fake_wait(300)
      category_selected = True

    # Check if posting an ad is allowed / possible
    fRc = post_ad_is_allowed(driver)
    if fRc is False:
        return fRc

    # Fill form
    if "type" in ad and ad["type"] == "WANTED":
        driver.find_element_by_id('adType2').click()
    title_input = driver.find_element_by_id('postad-title')
    title_input.click()
    title_input.send_keys(ad["title"])
    driver.find_element_by_id('pstad-descrptn').click() # click description textarea to lose focus from title field which will trigger category auto detection
    if not category_selected:
      # wait for category auto detection
      try:
        WebDriverWait(driver, 3).until(lambda driver: driver.find_element_by_id('postad-category-path').text.strip() != '')
        category_selected = True
      except:
        pass
      # Change category if present in config (otherwise keep auto detected category from eBay Kleinanzeigen)
      cat_override = ad["caturl"]
      if cat_override:
        cat_override = cat_override.replace('p-anzeige-aufgeben', 'p-kategorie-aendern') # replace old links for backwards compatibility
        driver.find_element_by_id('pstad-lnk-chngeCtgry').click()
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.ID, 'postad-step1-sbmt')))
        driver.get(cat_override)
        fake_wait()
        driver.find_element_by_id('postad-step1-sbmt').submit()
        fake_wait()
        category_selected = True
      if not category_selected:
        raise Exception('No category configured for this ad and auto detection failed, cannot publish')

    # add additional category fields
    additional_category_options = ad.get("additional_category_options", {})
    for element_id, value in additional_category_options.items():
        try:
            select_element = driver.find_element_by_css_selector(
                'select[id$="{}"]'.format(element_id)
            )
            Select(select_element).select_by_visible_text(value)
        except NoSuchElementException:
            try:
                driver.find_element_by_xpath("//input[@id='%s']" % element_id).send_keys(value)
            except NoSuchElementException:
                pass


    text_area = driver.find_element_by_id("pstad-descrptn")
    ad_suffix = config.get("glob_ad_suffix", "")
    ad_prefix = config.get("glob_ad_prefix", "")

    if ad.get("description_file", None) is not None:
        description_file = ad.get("description_file")
        with open(description_file, "r", encoding="utf-8") as f:
            description_lines = f.readlines()
    else:
        desc = ad.get("desc")
        description_lines = desc.split("\\n")

    description_lines = [x.strip("\\n") for x in description_lines]
    description_lines.append(ad_suffix)
    description_lines.insert(0, ad_prefix)

    for p in description_lines:
        text_area.send_keys(p)

    fake_wait()

    if (ad['shipping_type']) != 'NONE':
        try:
            if (ad['shipping_type']) == 'PICKUP':
                ship_button = driver.find_element_by_xpath("/html/body/div[1]/form/fieldset[2]/div[3]/div/div/div[1]/div[1]/div[2]/div/label[2]/input")
                ship_button.click()
            if (ad['shipping_type']) == 'SHIPPING':
                select_element = driver.find_element_by_css_selector('select[id$=".versand_s"]')
                shipment_select = Select(select_element)
                shipment_select.select_by_visible_text("Versand möglich")
            fake_wait()
        except NoSuchElementException:
            pass

    text_area = driver.find_element_by_id('pstad-price')
    if ad["price_type"] != 'GIVE_AWAY':
        text_area.send_keys(ad["price"])
        try:
            price = driver.find_element_by_xpath("//input[@name='priceType' and @value='%s']" % ad["price_type"])
        except NoSuchElementException:
            try:
                price = driver.find_element_by_xpath("//select[@name='priceType']/option[@value='%s']" % ad["price_type"])
            except NoSuchElementException:
                raise Exception('Cannot find price type selection!')        
    price.click()
    fake_wait()

    text_area = driver.find_element_by_id('pstad-zip')
    text_area.clear()
    if ad.get("zip", None) is not None:
        text_area.send_keys(ad["zip"])
    else:
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
                uploaded_count = len(driver.find_elements_by_class_name("imagebox-new-thumbnail"))
                log.debug("\tUploading image: %s" % path_abs)
                fileup.send_keys(os.path.abspath(path_abs))
                total_upload_time = 0
                while uploaded_count == len(driver.find_elements_by_class_name("imagebox-new-thumbnail")) and \
                        total_upload_time < 30:
                    fake_wait(500)
                    total_upload_time += 0.5

                if uploaded_count == len(driver.find_elements_by_class_name("imagebox-new-thumbnail")):
                    log.warning("\tCould not upload image: %s within %s seconds" % (path_abs, total_upload_time))
                else:
                    log.debug("\tUploaded file in %s seconds" % total_upload_time)
        except NoSuchElementException:
            pass

    # Upload images from directory
    if "photo_dir" in ad:
        try:
            fileup = driver.find_element_by_xpath("//input[@type='file']")
            path = ad["photo_dir"]
            path_abs = os.path.join(config["glob_photo_path"], path)
            if not path_abs.endswith("/"):
                path_abs += "/"
            for filename in sorted(os.listdir(path_abs)):
                if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".gif")):
                    continue
                file_path_abs = path_abs + filename
                uploaded_count = len(driver.find_elements_by_class_name("imagebox-new-thumbnail"))
                log.debug("\tUploading image: %s" % file_path_abs)
                fileup.send_keys(os.path.abspath(file_path_abs))
                total_upload_time = 0
                while uploaded_count == len(driver.find_elements_by_class_name("imagebox-new-thumbnail")) and \
                        total_upload_time < 60:
                    fake_wait(1000)
                    total_upload_time += 1
                
                if uploaded_count == len(driver.find_elements_by_class_name("imagebox-new-thumbnail")):
                    log.warning("\tCould not upload image: %s within %s seconds" % (file_path_abs, total_upload_time))
                else:
                    log.debug("\tUploaded file in %s seconds" % total_upload_time)
        except NoSuchElementException as e:
            log.error(e)

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
            submit_button = driver.find_element_by_id('pstad-submit')
            if submit_button:
                submit_button.click()
        except NoSuchElementException as e_msg:
            log.debug(e_msg)
            pass
        
        WebDriverWait(driver, 6).until(EC.url_contains('adId='))
        
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

    options = webdriver.ChromeOptions()

    if config.get('headless', False) is True:
        log.info("Headless mode")
        options.add_argument("--headless")

    if os.path.isfile("./chrome-win/chrome.exe"):
        log.info("Found ./chrome-win/chrome.exe")
        options.binary_location = "./chrome-win/chrome.exe"

    #options.add_extension(r'E:\Google Drive\Verkauf\_auto\ebayKleinanzeigen\chrome-extensions\crobot.crx')

    driver = webdriver.Chrome(options=options)

    stealth(driver,
        languages=["en-US", "en"],
        vendor="Google Inc.",
        platform="Win32",
        webgl_vendor="Intel Inc.",
        renderer="Intel Iris OpenGL Engine",
        fix_hairline=True,
        )
    log.info("New session is: %s %s" % (driver.session_id, driver.command_executor._url))

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

    if config.get("headless") is None:
        config["headless"] = False

    updateInterval = config.get("update_interval", 4)

    fForceUpdate = False
    fDoLogin = True

    dtNow = datetime.utcnow()

    driver = session_create(config)
    profile_write(sProfile, config)
    login(config)
    fake_wait(randint(1000, 4000))
    for ad in config['ads']:
        assert len(ad["title"]) > 9, "eBay restriction: Title must be at least 10 chars long"

    for ad in config["ads"]:

        fNeedsUpdate = False

        log.info("Handling '%s'" % ad["title"])

        if "date_updated" in ad:
            # python < 3.7 do not support datetime.datetime_fromisoformat()
            # https://stackoverflow.com/a/60852111/256002
            if int(python_version_tuple()[1]) < 7:
                from backports.datetime_fromisoformat import MonkeyPatch
                MonkeyPatch.patch_fromisoformat()

            dtLastUpdated = datetime.fromisoformat(ad["date_updated"])
        else:
            dtLastUpdated = dtNow
        dtDiff = dtNow - dtLastUpdated

        if "enabled" in ad and ad["enabled"] == "1":
            if "date_published" in ad:
                log.info("\tAlready published (%d days ago)" % dtDiff.days)
                if dtDiff.days > updateInterval:
                    fNeedsUpdate = True
            else:
                log.info("\tNot published yet")
                fNeedsUpdate = True
        else:
            log.info("\tDisabled, skipping")

        if fNeedsUpdate or fForceUpdate:

            # delete ad if it was published already
            if "id" in ad or "date_published" in ad:
                delete_ad(driver, ad)

            fPosted = post_ad(driver, ad, True)
            if not fPosted:
                break

            log.info("Waiting for handling next ad ...")
            fake_wait(randint(2000, 6000))

        profile_write(sProfile, config)

    driver.close()
    log.info("Script done")