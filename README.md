# ebayKleinanzeigen

## Prerequisites

* config.json (from config.json.example)
* geckodriver (to /usr/local/bin): https://github.com/mozilla/geckodriver/releases
* selenium: ```pip install selenium```

## Features

- **New** Upload all images from a set subdirectory
- **New** Configure shipping type in ad config
- Automatically deletes and re-publishes ad if existing one is too old
- Keeps track of ad publishing and last updating date
- Ability to selectively enable / disable ads being published / updated
- Overrides auto detected category (if `caturl` is specified) and fills the form data
- Uploads multiple photos

## Installation guide (Ubuntu)

1. Install Python 3 and PIP

    `sudo apt-get install python3 python3-pip`

2. Install Selenium

    `pip3 install selenium`

3. Install Gecko Driver and move it to /usr/bin

- Check the [release Page](https://github.com/mozilla/geckodriver/releases) of Mozilla and replace #RELEASE# with the current release number, e.g. v0.26.0

    `wget https://github.com/mozilla/geckodriver/releases/download/#RELEASE#/geckodriver-#RELEASE#-linux64.tar.gz`

- Extract the file

    `tar xzf geckodriver-#RELEASE#-linux64.tar.gz`

- Move the driver to it's prefered location

    `sudo mv geckodriver /usr/bin/geckodriver `

4. clone the app from git

    `git clone https://github.com/donwayo/ebayKleinanzeigen`

5. configure the app

- go to the Project-Folder

- copy the sample to a new file

   `cp config.json.example config.json`

- edit the file and fill in your details. 

- to find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category. 

6. Start the app

- got to the app folder

    `python3 kleinanzeigen.py --profile config.json`

Now a browser window should start, login and fill the fields automatically. 

## Credits
- @Lopp0 - initial script
- @donwayo - Fixes and improvements
- @MichaelKueller - Python 3 migration and cleanup
- @n3amil - Fixes and improvements
- @x86dev - Fixes and improvements
- @neon-dev - Fixes and improvements
- @kahironimashte - Install guide
