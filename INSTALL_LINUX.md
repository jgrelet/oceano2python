# Linux installation

``` bash
> python -m pip install --upgrade pip

> pip list
Package    Version
---------- -------
pip        19.1
setuptools 40.8.0

> pip list --user

> pip install pylint
> pip install toml
> pip install netCDF4
> pip install matplotlib
> pip install numpy
> pip install seawater
> pip install PyInstaller
> pip install ConfigParser
```

## basemap installation

``` bash
> sudo apt-get install libgeos-3.5.0 libgeos-c1v5 libgeos-dev
> sudo -H python3 -m pip install basemap-v1.1.0.tar.gz 

Installing collected packages: pyproj, pyshp, basemap
Successfully installed basemap-1.1.0 pyproj-2.1.2 pyshp-2.1.0
```

Clone the latest version of PySimpleGUI

``` bash
> git clone https://github.com/PySimpleGUI/PySimpleGUI.git 
```

and add the path of PySimpleGUI directory to $PYTHONPATH env

If you want use QT instead of Tk, replace:

``` bash
import PySimpleGUI as gs
```

by

``` bash
import PySimpleGUIQt as gs
```