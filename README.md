
---

##  Features

- Clone all channels (text, voice, categories)
- Clone roles and permissions
- Clone server settings
- Fast and simple to use

---

##  Requirements

- Python 3.8 or higher
- `discord.py-self` (NOT the regular `discord.py`)

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/poixt/discord-server-cloner.git
cd discord-server-cloner
```

---

### 2.  IMPORTANT — Uninstall Conflicting Packages First

Before installing dependencies, you **must** remove any existing Discord libraries to avoid conflicts:

```bash
pip uninstall discord discord.py -y
```

Then install the correct self-bot library:

```bash
pip install discord.py-self
```

---

### 3. Install All Requirements

```bash
pip install -r requirements.txt
```

---

##  Linux Setup

```bash

sudo apt update
sudo apt install python3 python3-pip git -y

git clone https://github.com/poixt/discord-server-cloner.git
cd discord-server-cloner

pip3 uninstall discord discord.py -y

pip3 install discord.py-self

pip3 install -r requirements.txt

python3 main.py
```

---

## 🪟 Windows Setup

```bat
:: Make sure Python is installed from https://python.org
:: Open Command Prompt (cmd) or PowerShell

:: Clone the repo (or download ZIP from GitHub)
git clone https://github.com/poixt/discord-server-cloner.git
cd discord-server-cloner

:: Remove conflicting packages
pip uninstall discord discord.py -y

:: Install correct library
pip install discord.py-self

:: Install requirements
pip install -r requirements.txt

:: Run the script
python main.py
```



---

##  Usage

1. Run the script:
   ```bash
   python main.py        # Windows
   python3 main.py       # Linux / macOS
   ```

2. Enter your **User Token** when prompted.

3. Enter the **Source Server ID** (the server you want to clone).

4. Enter the **Target Server ID** (the server you want to clone into).

5. Let it run 

---

##  How to Get Your User Token

1. Open Discord in your **browser** (not the app).
2. Press `Ctrl + Shift + I` to open DevTools.
3. Go to the **Network** tab.
4. Press `Ctrl + R` to reload.
5. Click on any request, go to **Headers**, and look for `Authorization` — that's your token.

---



---

##  Credits

Made by [poixt](https://github.com/poixt)
