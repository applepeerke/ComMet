# Introduction
ComMet stands for `Com`pare `Met`hods. It compares methods of different python projects and lists the differences.
It works on Mac, Windows (and probably Linux too).


# Getting started
There are several possibilities.
## a. The Easy Way
You can download the executable directly from GitHub. \
Optionally move or copy this executable to a desired location like `Apps` (Mac) or `Program Files` (Windows). \
ComMet will start if jou doubleclick on the executable.

## b. From command prompt (CLI)
### Requirements
- python 3.12
- pysimplegui
### Start ComMet
Start the command prompt and  `cd` to ComMet subfolder `src`.
Type `python commet.py` and press `Return`.
De app starts with a display.
## c. Create app from source code
From the source code you can create an app. This is an .app (Mac) or .exe (Windows) file.
### Requirements
- python 3.12
- pysimplegui
- pyinstaller

### General
- Log in as an administrator
- Start Terminal and `cd` to the ComMet main folder (the folder that contains subfolder `src`)

### Mac
- On Mac, type `pyinstaller Geldmaatje.py --onefile --windowed  --clean --noconfirm -i "src/logo.icns" --add-data resources:resources` and press `Return`

### Windows
- On Windows, type `pyinstaller Geldmaatje.py --onefile --windowed  --clean --noconfirm -i src\logo.ico --add-data resources:resources` and press `Return`

If all went well a subfolder `dist` has been created in folder `src`. Here you can find the executable `.app` or `.exe` file. \
You can proceed as described at `a.`.