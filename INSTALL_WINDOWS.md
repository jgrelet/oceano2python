# Windows installation

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

Installing basemap on Windows from source could be tricky. A simple solution is to install the  [Wheels](https://pip.pypa.io/en/latest/user_guide/#installing-from-wheels) (*.whl) binary from the URL:
[https://www.lfd.uci.edu/~gohlke/pythonlibs/](https://www.lfd.uci.edu/~gohlke/pythonlibs/)

Select and download locally the binary Wheels file `basemap-1.2.0-cp37-cp37m-win_amd64.whl`

and install it from Wheels

``` bash
> pip install basemap-1.2.0-cp37-cp37m-win_amd64.whl
```

Clone the latest version of PySimpleGUI

``` bash
> git clone https://github.com/PySimpleGUI/PySimpleGUI.git 
```

and add the path of PySimpleGUI directory to $PYTHONPATH env