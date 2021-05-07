# ebayKleinanzeigen

## Prerequisites

* config.json (from config.json.example)
* geckodriver (to /usr/local/bin): <https://github.com/mozilla/geckodriver/releases>
* selenium: ```pip install selenium```

## Features

* **New** Use Chromium with selenium_stealth to overcome blank login page.
* Upload all images from a set subdirectory
* Configure shipping type in ad config
* Automatically deletes and re-publishes ad if existing one is too old
* Keeps track of ad publishing and last updating date
* Ability to selectively enable / disable ads being published / updated
* Overrides auto detected category (if `caturl` is specified) and fills the form data
* Uploads multiple photos

## Installation Guide (Linux)

Run the following in your terminal or consult the step by step instructions below it.

```bash
# install python 3 and pip
sudo apt-get install python3 python3-pip
# install selenium, selenium_stealth and other requirements
pip3 install -r requirements.txt
# clone the repo
git clone git@github.com:donwayo/ebayKleinanzeigen.git && cd ebayKleinanzeigen/
# clone the template config file
cp config.json.example config.json
# edit the configuration
$EDITOR config.json
# start the app
python3 kleinanzeigen.py --profile config.json
```

1. Install Python 3 and PIP
    `sudo apt-get install python3 python3-pip`
2. Install Selenium
    `pip3 install selenium`
3. clone the app from git
    `git clone https://github.com/donwayo/ebayKleinanzeigen`
4. configure the app
   * go to the Project-Folder
   * copy the sample to a new file
      `cp config.json.example config.json`
   * edit the file and fill in your details.
   * to find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.
5. Start the app
   * go to the app folder
      `python3 kleinanzeigen.py --profile config.json`
   * if launching from VS Code, the following path variable should be set when not in headless mode:
      `export DISPLAY=":0"` ([source](https://stackoverflow.com/a/61672397/256002))

Now a browser window should start, login and fill out the fields automatically.

## Installation Guide (MacOS)

```bash
# create new virtual env, for instance with conda
conda create --name ebayKleinanzeigen python=3.7
conda activate ebayKleinanzeigen
pip install selenium selenium_stealth

git clone https://github.com/donwayo/ebayKleinanzeigen

# open config and enter your preferences. For cat_url, see below
cp config.json.example config.json
```

* To run the app, run `python kleinanzeigen.py --profile config.json`

* to find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.

Now a browser window should start, login and fill the fields automatically.

## Installation Guide (Windows)

1. Install Chrome for Windows
2. Install Python 3 with the Windows 10 App Store
3. create a `ebayKleinanzeigen` directory somewhere you want
4. download chrome driver https://chromedriver.storage.googleapis.com/90.0.4430.24/chromedriver_win32.zip and unzip in ebayKleinanzeigen directory
5. download the ebayKleinanzeigen app from git and extract it to the ebayKleinanzeigen directory
6. configure the app
   * go to the ebayKleinanzeigen directory
   * copy the sample to a new file
      `cp config.json.example config.json`
   * edit the file and fill in your details.
   * to find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.
7. open Windows PowerShell by left mouse click on Windows Start and then klick Windows PowerShell
8. PowerShell install python selenium stealth with this command
    `python3 -m pip install selenium_stealth`
7. Start the app in PowerShell
   * go to the ebayKleinanzeigen directory
      `python3 kleinanzeigen.py --profile config.json`

Now a browser window should start, login and fill the fields automatically.

## Additional Category fields

|   |   | |
|---|---| ---|
| Elektronik > Foto  | `foto.art_s`         | `Kamera`, `Objektiv`, `Zubehör`, `Kamera & Zubehör` |
| Elektronik > Foto  | `foto.condition_s`   | `Neu`, `Gebraucht`, `Defekt`          |

## Credits

* @Lopp0 - initial script
* @donwayo - Fixes and improvements
* @MichaelKueller - Python 3 migration and cleanup
* @n3amil - Fixes and improvements
* @x86dev - Fixes and improvements
* @neon-dev - Fixes and improvements
* @kahironimashte - Install guide
* @therealsupermario - Description Files, ad-level zip codes, custom update interval, support for additional category fields
* @denisergashbaev - python 3.6 fixes, README.md, running from VS Code
