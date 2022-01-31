> Development of this client has been stopped. Please use https://github.com/Second-Hand-Friends/kleinanzeigen-bot

# ebayKleinanzeigen

## Prerequisites

* Python 3 and pip
* Chrome or Chromium
* ChromeDriver for your specific Chrome/Chromium version

## Features

* Upload all images from a set subdirectory
* Configure shipping type in ad config
* Automatically deletes and re-publishes ad if existing one is too old
* Keeps track of ad publishing and last updating date
* Ability to selectively enable / disable ads being published / updated
* Overrides auto detected category (if `caturl` is specified) and fills the form data
* Uploads multiple photos

## Installation Guide (Linux)

1. Install Python 3 and PIP:  
   `sudo apt install python3 python3-pip`
2. Clone the app from git and switch into the newly created directory:  
   `git clone https://github.com/donwayo/ebayKleinanzeigen && cd ebayKleinanzeigen`
3. Install required packages:  
   `pip3 install -r requirements.txt`
4. Install Chromium **(skip this step if you have Chrome or Chromium installed already)**:  
   `sudo apt install chromium-browser`
5. Install ChromeDriver:  
   `sudo apt install chromium-chromedriver`  
   Or, if your version of Chrome/Chromium does not automatically update, download the corresponding [ChromeDriver](https://chromedriver.chromium.org/downloads) for your installed version. Then extract the binary into the ebayKleinanzeigen directory and don't forget `chmod +x chromedriver`.
6. Configure the app:
   * Copy the sample to a new file:  
     `cp config.json.example config.json`
   * Edit the file and fill in your details.
   * To find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.
7. To run the app, run `python3 kleinanzeigen.py --profile config.json`  
   If launching from VS Code, the following path variable should be set when not in headless mode:  
   `export DISPLAY=":0"` ([source](https://stackoverflow.com/a/61672397/256002))

Now a browser window should start, login and fill the fields automatically.

## Installation Guide (MacOS)

1. Install a specific version of Chromium from https://chromium.cypress.io/mac/
2. Add the executable to the `PATH`
3. Run these steps:  
   ```zsh
   brew install chromedriver
   
   # create new virtual env, for instance with conda
   conda create --name ebayKleinanzeigen python=3.7
   conda activate ebayKleinanzeigen
   
   git clone https://github.com/donwayo/ebayKleinanzeigen
   cd ebayKleinanzeigen
   pip3 install -r requirements.txt
   
   cp config.json.example config.json
   ```
4. Open config.json and enter your preferences. For cat_url, see below  
   To find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.
5. To run the app, run `python kleinanzeigen.py --profile config.json`

Now a browser window should start, login and fill the fields automatically.

## Installation Guide (Windows)

1. Install Python 3 from [here](https://www.python.org/downloads/) or from the Windows 10 App Store
2. Download the latest ebayKleinanzeigen version via `git clone https://github.com/donwayo/ebayKleinanzeigen.git && cd ebayKleinanzeigen`  
   Or, if you don't have git installed, as a zip from [here](https://github.com/donwayo/ebayKleinanzeigen/archive/refs/heads/master.zip) and extract it, then open the extracted directory.
3. Open a command prompt (CMD, PowerShell or Git Bash) inside the ebayKleinanzeigen directory, then install the required Python packages:  
   `python3 -m pip3 install -r requirements.txt`
4. Install Chrome for Windows  
   Or, if you don't want to install Chrome, download the latest version of Chromium from [here](https://download-chromium.appspot.com/) and copy the number after "Build Revision: " to your clipboard without leading or trailing whitespaces for the next step. Extract the zip and copy the `chrome-win` folder over to the ebayKleinanzeigen directory.
5. Download ChromeDriver for your version of Chrome from [here](https://chromedriver.chromium.org/downloads)  
   In case of Chromium, you can get it by replacing the `BUILD_REVISION` in this link with the number you just copied in the last step: `https://commondatastorage.googleapis.com/chromium-browser-snapshots/index.html?prefix=Win/BUILD_REVISION/`. The archive you need to download is named chromedriver_win32.zip.
6. Extract and copy chromedriver.exe to the ebayKleinanzeigen directory
7. Configure the app
   * Copy `config.json.example` to a new file named `config.json`
   * Edit `config.json` and fill in your details
   * To find out the categories you need to start posting an ad on the website and then copy the corresponding link to the category from there. It's the screen where you select the category.
8. To run the app, run `python3 kleinanzeigen.py --profile config.json` in the command prompt.

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
