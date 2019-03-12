Sous Windows, VSCode et Python 3.7.2
> pip3
Fatal error in launcher: Unable to create process using '"'
[ntird-us191-jg4:jgrelet]/c/git/python/pirata
> python3 -m pip install --upgrade pip
...
Successfully installed pip-19.0.3
[ntird-us191-jg4:jgrelet]/c/git/python/pirata
> pip install toml
Collecting toml
  Downloading https://files.pythonhosted.org/packages/a2/12/ced7105d2de62fa7c8fb5fce92cc4ce66b57c95fb875e9318dba7f8c5db0/toml-0.10.0-py2.py3-none-any.whl
Installing collected packages: toml
Successfully installed toml-0.10.0

Il est prefereable d'installer la derniere version Python 3.7.2

Configuration du fichier setting.json de jgrelet:

// Placez vos paramètres dans ce fichier pour remplacer les paramètres par défaut
{
    "go.gopath": "C:/Users/jgrelet/go",
    "go.goroot": "c:/go",
    "git.path": "C:\\Program Files\\Git\\bin",
    //"terminal.integrated.shell.windows": "C:\\Windows\\sysnative\\cmd.exe",
    //"terminal.integrated.shellArgs.windows": ["/K", "C:\\opt\\cmder\\vscode.bat"],
    //"terminal.integrated.shell.windows": "C:\\msys64\\usr\\bin\\bash.exe",
    "terminal.integrated.shell.windows": "C:\\MinGW\\msys\\1.0\\bin\\bash.exe",
    //"terminal.integrated.shellArgs.windows": ["--login", "-i"],
   // "terminal.integrated.cwd": "/c/Users/jgrelet/go/src/bitbucket.org/jgrelet/raspberry/go/go-serial",
    //"terminal.integrated.shell.windows": "C:\\Windows\\sysnative\\cmd.exe",
    //"terminal.integrated.shellArgs.windows": ["/k", "C:\\opt\\TDM-GCC-64\\mingwvars.bat"],
    "matlab.mlintpath": "C:\\Program Files\\MATLAB\\R2016b\\bin\\win64\\mlint.exe",
    "files.associations": {
        "*.m": "matlab"
    },
   // "vim.enableNeovim": false,
    //"http.proxy": "http://antea:3128"
    "workbench.colorTheme": "Visual Studio Dark",
    "go.liveErrors": {
        "enabled": true,
        "delay": 500
    },
    "git.autofetch": true,
    "git.enableSmartCommit": true,
    "explorer.confirmDelete": false,
    "team.showWelcomeMessage": false,
    //"files.autoSave": "afterDelay"
}

Pour utiliser le bash de git, modifier la ligne:
    "terminal.integrated.shell.windows": "C:\\MinGW\\msys\\1.0\\bin\\bash.exe",
par
    "terminal.integrated.shell.windows": "C:\\Program Files\\Git\\bin\\bash.exe",
    
Add in user setting.json:
  "[python]": {
        "editor.insertSpaces": true,
        "editor.tabSize": 4
    }

In setting.json:

    "python.linting.pylintEnabled": true,
    "python.linting.enabled": true,
    "python.linting.mypyEnabled": false,
    "python.pythonPath": "C:\\opt\\python\\python3.7\\python.exe",
    "editor.formatOnSave": true,
    "editor.formatOnType": true,
    "python.autoComplete.addBrackets": true,
    "editor.formatOnPaste": true

Modules pYthon à intaller:
--------------------------
Autoformatting
----------------------
> pip install autopep8
Installer l'extension Python-autopep8
Cmd+P choisir autopip
> pip install pylint

Developpement:
> pip install pynmea2
> pip install pySerial
> pip install netCDF4
> pip install seawater
> pip install numpy
