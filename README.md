# Qmix pump and valve interface

[![Travis-CI Build Status](https://travis-ci.org/psyfood/pyqmix.svg?branch=master)](https://travis-ci.org/psyfood/pyqmix)
[![Latest PyPI Release](https://img.shields.io/pypi/v/pyqmix.svg)](https://pypi.org/project/pyqmix/)
[![Conda Version](https://img.shields.io/conda/vn/conda-forge/pyqmix.svg)](https://anaconda.org/conda-forge/pyqmix)

This Python package wraps the Cetoni Qmix pump and valve interface DLLs using
CFFI. Supports both Python 2 and 3.

## Table of Contents

- [Quick installation instructions](#quick-installation-instructions)
- [Gustometer Setup](#gustometer-setup)
- [Operate pumps via pyqmix-web](#operate-pumps-via-pyqmix-web) _(no installation required)_
- [Install Python and pyqmix](#install-python-and-pyqmix)
- [Operate pumps via pyqmix](#operate-pumps-via-pyqmix) _(requires installation)_
- [Best Practices](#best-practices)
- [Citation](#citation)

## Quick installation instructions


If you already installed the Cetoni QmixSDK, created a device configuration via QmixElements, and are familiar with Python, you may simply install `pyqmix` via `conda` from `conda-forge`. To create a new `conda` environment for `pyqmix`, named `nemesys`, run
```
conda create -n nemesys -c conda-forge pyqmix
```

from the command line. This is the recommended installation procedure, because it ensures the installation of `pyqmix` and all of its dependencies will not alter any existing `conda` environment.

To install `pyqmix` into an *existing* `conda` environment, run

```
conda install -c conda-forge pyqmix
```
However, we suggest you always create a new, dedicated environment instead.

Of course, you may also install `pyqmix` via good ol' `pip`:

```
pip install pyqmix
```

If you have no idea what this is all about, we suggest you follow the procedures described below.

## Gustometer Setup

### Find the CD and license code
Open the paper-folder you received from CETONI. In the folder you will find a license key and a CD with:
 - Software: QmixElements and QmixSDK
- QmixElements Manual in Doc/Software, which specifies system requirements and how to install the software

### Prepare your computer
Set up system requirements on your computer as described in the documentation. Refer to QmixElements manual:
- Disable standby or sleep mode
- Disable power saving for USB ports in the power options of the Control Panel

### Install QmixElements
- Insert the CD from CETONI in your computer. 
- Start the QmixElements_Setup_v###.exe application file as administrator
- During installation, accept to install VCI (VCI Driver)
- In case you get a Windows Security Warning -> Trust software from HMS Technology Center Ravensburg GmbH. 

### Install QmixSDK
- Install the QmixSDK you received on the CD from CETONI. pyqmix is tested to work with QmixSDK versions 20180626 and later. If your version of QmixSDK is older than that, please contact Cetoni to retrieve an updated version.
- Restart the computer

### Connect the pump system to the computer
- Connect the base module to computer
- Connect power supply to base module
- Connect the base module to the computer via the supplied USB cable.

### Create a Device Configuration
- Open QmixElements
- Activate License
  - Edit -> Activate Licence -> [enter License Key] -> click OK. The License key is found by the CD in the folder provided by CETONI.
- Create the actual Device Configuration
    - Device -> Create Configurations -> you are then asked: `Would you like to update your local device database devices.db with a new one?`. If you have a devices.db file on the installation CD from CETONI, then click the `Yes` button and browse for the file.  
From the device list drag all the items you want to configure to the ‘Device Configuration’ which is the large empty black area to the left of the QmixElements software. You do not need to configure the base module.
- Save configuration
  - File -> save.
- Right-click on the first item in the Device Configuration (the one furthest to the left), select ‘Configure’ and follow the instructions. Repeat the procedure for each item in the Device Configuration. 
- Save configuration at the end. 

## Operate pumps via pyqmix-web
The user-visible part of pyqmix-web runs in the web browser. You need a modern browser to run the application. Recent versions of Chrome, Firefox, and Safari work well; Microsoft Internet Explorer is not supported.

- Download the latest pyqmix-web release from https://github.com/psyfood/pyqmix-web/releases (you will want to get the `.exe` file).
- Run the `.exe` file

## Install Python and pyqmix
### Install Anaconda Python
- Install the Anaconda Python distribution if it is not installed already. You can download it from https://www.anaconda.com/download/. Get the "Python 3.x" version.
- During setup, skip the installation of Microsoft VSCode
- Otherwise just accept the default settings

### Create a new Python environment
Create a new `conda` Python environment called `nemesys` and install the required packages into this environment.
- Click the Windows button / Open the “Start” menu
- Open the Anaconda Prompt. This will open a command line window which is correctly set up to use your Anaconda Python installation.
- Create the `nemesys` Python environment and install `pyqmix` as well as the [Spyder](https://www.spyder-ide.org) development environment:
  - Type: `conda create -n nemesys python=3 pyqmix spyder`

## Operate pumps via pyqmix
### Open and run scripts
- Open the Anaconda Prompt as described above.
- Activate the `nemesys` environment
  - Type: `activate nemesys`
- Start the Spyder development environment:
  - Type: `spyder`
- Open the [example scripts](https://github.com/psyfood/pyqmix/tree/master/pyqmix/examples), run and modify them.
- Have fun!

## Best Practices

The setup of the pump system and best practices are described in our paper (see reference below).
Additionally, we suggest the following procedures the improve reliability and ease of use:

- Make sure output tubes are of equal length to ensure that the stimulus onset is identical for all pumps.
- Ensure that tube cuts are clean and straight, perpendicular to the tube. This can be achieved by using so-called tube-cutters. 
- The 50 mL glass syringes fit really tightly into the syringe holders.Especially when new, it might have to push relatively hard to actually insert the syringe into the holder. This will get easier over time, as the syringe and holders “grind in”.
- Glass syringes might break if too much pressure is exerted. Ensure that the syringes are attached tightly to using the the syringe holders and syringe piston holders, but don’t tighten the syringe holder too much as it can smash the syringe glass cylinder.
- Remove air bubbles. We developed a new procedure that is implemented in pyqmix-web and will guide the user through the process.

## Citation

If you use this software, please cite our publication:

>   [Andersen, Camilla Arndal, Alfine, Lorenzo, Ohla, Kathrin, & Höchenberger, Richard. (_in press_). A new gustometer: Template for the construction of a portable and modular stimulator for taste and lingual touch. _Behavior Research Methods_. doi: 10.3758/s13428-018-1145-1](https://doi.org/10.3758/s13428-018-1145-1)

A [pre-print]( http://doi.org/10.5281/zenodo.1456663) is available from Zenodo.

