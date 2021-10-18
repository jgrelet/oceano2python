Aide mémoire Python
-------------------
J Grelet June 2011 - March 2019 - Avril 2021

Conda:
-------
Installer miniconda

> conda config --add channels conda-forge

Once the conda-forge channel has been enabled, matplotlib, matplotlib-base, mpl_sample_data can be installed with:

> conda install matplotlib matplotlib-base mpl_sample_data

It is possible to list all of the versions of matplotlib available on your platform with:

> conda search matplotlib --channel conda-forge

Installation based on an YAML environment file

> conda env create -f environment<OS>.yml -n <new_env_name>

example:

> conda env create -f environment-windows.yml -n ms1

Export your environment

Duplicate your environment on other computer or OS, just export it to a YAML file:

>conda env export --no-builds > environment-windows.yml


Les listes:
-----------
Collection d'objet
L=[]
L=[1,2,3,4]
L[2:]
[3,4]
L[:-1]
[1, 2, 3]
L[::-1]
[4, 3, 2, 1]
L.method()  avec method = append, sort,index,reverse, extend

We see that extend() is semantically clearer, and that it can run much faster than append(), 
when you intend to append each element in an iterable to a list.
If you only have a single element (not in an iterable) to add to the list, use append.

The following two snippets are semantically equivalent:
for item in iterator:
    a_list.append(item)
and
a_list.extend(iterator)

The latter may be faster as the loop is implemented in C.

List comprehensions:
------------------------------------------
new_list = [expression for_loop_one_or_more condtions]

numbers = [1, 2, 3, 4]
squares = [n**2 for n in numbers]
print(squares) # Output: [1, 4, 9, 16]

list_a = [1, 2, 3]
square_cube_list = [ [a**2, a**3] for a in list_a]
print(square_cube_list) # Output: [[1, 1], [4, 8], [9, 27]]

Tuples:
-------
Un tuple est équivalent à une liste masi il n'est pas modifiable
T=(1,2,3)
T[1]
2
T[1]=5
TypeError: 'tuple' object does not support item assignment

Dictionnaires:
--------------
Tables non ordonnées de référence d'objets
>>> D={}
>>> D={'un': 1, 'deux': 2}
>>> D['un']
1
>>> 'deux' in D
True
>>> D.keys()
dict_keys(['un', 'deux'])
>>> list(D.keys())
['un', 'deux')]
>>> D.values()
dict_values([1, 2])
>>> list(D.values())
[1, 2]
>>> len(D)      Return the number of items in the dictionary d.
2
>>> d[key]      Return the item of d with key key. Raises a KeyError if key is not in the map.
    
>>> d[key] = value        Set d[key] to value.

>>> del d[key]            Remove d[key] from d. Raises a KeyError if key is not in the map.

>>> key in d              Return True if d has a key key, else False.

>>> key not in d          Equivalent to not key in d.

>>> iter(d)               Return an iterator over the keys of the dictionary. This is a shortcut for iter(d.keys()).

>>> d.clear()             Remove all items from the dictionary.

>>> d.copy()              Return a shallow copy of the dictionary.

classmethod fromkeys(seq[, value])
    Create a new dictionary with keys from seq and values set to value.
    fromkeys() is a class method that returns a new dictionary. value defaults to None.

get(key[, default])
    Return the value for key if key is in the dictionary, else default. If default is not given, it defaults to None, so that this method never raises a KeyError.

items()
    Return a new view of the dictionary’s items ((key, value) pairs). See the documentation of view objects.

keys()
    Return a new view of the dictionary’s keys. See the documentation of view objects.

pop(key[, default])
    If key is in the dictionary, remove it and return its value, else return default. If default is not given and key is not in the dictionary, a KeyError is raised.

popitem()
    Remove and return an arbitrary (key, value) pair from the dictionary.

    popitem() is useful to destructively iterate over a dictionary, as often used in set algorithms. If the dictionary is empty, calling popitem() raises a KeyError.

setdefault(key[, default])
    If key is in the dictionary, return its value. If not, insert key with a value of default and return default. default defaults to None.

update([other])
    Update the dictionary with the key/value pairs from other, overwriting existing keys. Return None.
    update() accepts either another dictionary object or an iterable of key/value pairs (as tuples or other iterables
    of length two). If keyword arguments are specified, the dictionary is then updated with those key/value pairs: 
    d.update(red=1, blue=2).

values()
    Return a new view of the dictionary’s values. See the documentation of view objects.

The objects returned from dict.keys(), dict.values(), and dict.items() are called dictionary views. 
They provide a dynamic view on the dictionary’s entries, which means that when the dictionary changes, 
the view reflects these changes. To force the dictionary view to become a full list use list(dictview). 


Fonctions spéciales:
--------------------
lambda: fonction anonyme
f = lambda a, b: a + b
f(1,2)
3

apply:  appelle des fonction avec des tuples en arguments
apply(f, (2,3)
5

map:    applique une fonction à chaque objet d'une séquence
def m(x): return x*2
map(m,[0,2,4]
[0, 4, 8]

print:  écrit sur la sortie standard
print "Class" + "Foo"
ClassFoo
print
print "Class %s is not = %d" % ('Foo', 1)
Class Foo is not = 1
print "Class %s is not = %d" % ('Foo', 1),

Classes et espace de nom (namespace):
-------------------------------------
import: récupère l'intégralité d'un module
from:   récupère certains noms d'un module
reload: recharge le module modifié

Notion importante lorsque l'on travaille dans l'interpréteur (python ou ipython)
L'import charge et exécute la première fois le code du module (fichier)
> cat simple.py
print "Hello"
spam = 1

>>> import simple   # importe charge et exécute la première fois le code du module
Hello
>>> simple.spam     # l'affectation a créé un attribut
1
>>> simple.spam = 2 # change l'attribut dans le module
>>> import simple   # récupère le module déjà chargé
>>> simple.spam     # le code n'a pas été exécuté de nouveau
2

Classe Foo déclarée dans un module foo, soit un fichier foo.py
import foo
f=foo.Foo()

from foo import Foo
f = Foo()

Les fonctions définies dans les classes ne sont accéssibles que via une instance
a=Foo()
a.dummy()
Foo().dummy()

Avec python, un attribut d'instance (membre) est une simple variable et existe 
dès qu'on lui affecte une valeur.
class Foo:
  def foo(self,value):
    self.attribut = value
    return self.attribut

Foo().foo(5)
5

Cet attribut peux également être initialisé (par défault) à la création de
l'instance par le constructeur __init__ (méthode appelée à la création d'un 
objet)
class Foo:
    def __init__(self,value=0):
        self.attribut = value
    def __repr__(self):
        return  "%d" % self.attribut
a=Foo()
a
0
a=Foo(5)
a
5


Attribut de classe
class Foo:
  foo = const

Attribut d'instance
class Foo:
  __init__(self, value)
    self.foo = value

En interne python associe les appels des méthodes d'instances aux méthodes de 
classes:
instance.methode(args,...) => class.methode(instance, args, ...)

Attributs privés d'une classe (utilise le name mangling)
self.__attribut => self._Class.__atribut

Attribut protected est passé en protégé (accessible aux fils mais pas en
dehors de l'objet) simplement en ajoutant "_" (a verifier)

Méthodes de classes liées:
class Foo:
   def foo(self, msg):
   print msg

o = Foo()
f = o.foo
f('Hello')

Méthodes de classes non liées (unbound):
o = Foo()
<__main__.Foo instance at 0x927e70c>
f = Foo.foo
<unbound method Foo.foo>
f(o,'Hello')
Hello

Les méthodes non liées requièrent un objet explicite

dictionary:
-----------
An associative array, where arbitrary keys are mapped to values. 
The keys can be any object with __hash__() and __eq__() methods. Called a hash in Perl.

Introspection:
--------------
Obtenir la liste des attribbuts d'une classe sous forme de dictionnaire:
o = Foo()
print o.__dict__

La liste des cles
print o.__dict__.keys()

La liste des valeurs
print o.__dict__.values()

Obtenir la liste des methodes et des attribbuts d'une classe:
print dir(o)

Determiner si les attributs d'un objet sont des methodes:
callable(o.<attribut>)
ex:
callable(o.name)
>>> True
type(o.name)
>>> <type 'instancemethod'>

Si une classe herite de object:
class foo(object):
print dir(o)
elle herite des methodes ['__class__','__setattr__', ....]
Liste des methodes:
methodList = [method for method in dir(object) if callable(getattr(object, method))]

Ajouter dynamiquement un attribut:
setattr(self, attributName, value)

Affecter dynamiquement un attribut (un dictionnaire ici):
setattr(self, attributName, {})
getattr(self, attributName)[key] = value

Remplir dynamiquement une l'equivalent C d'une structure en Python:
class bunch:
  def __init__(self, **kwds):
    self.__dict__.update(kwds)

s = bunch()                     # initialisation
s = bunch(k1=v1, k2=v2, ....)   # initialisation
s.k1 = v1
s.k2 = v2

avec l'exemple precedent:
setattr(self, s, {})
getattr(self, s)[k1] = v1
self.s[key].value             

Decorator:
-----------
A function returning another function, usually applied as a function transformation using the @wrapper syntax. 
Common examples for decorators are classmethod() and staticmethod().
The decorator syntax is merely syntactic sugar, the following two function definitions are semantically equivalent:

def f(...):
    ...
f = staticmethod(f)

@staticmethod
def f(...):
    ...


Ipyton:
-------
Pour changer de repertoire
cd path

Pour lancer un script
run script.py

Recharger un module: 
import module ne charge le module que la premiere fois
faire un reload(module) apres modification du code

Installer ZCA (Zope Component Architecture)
-------------------------------------------
Depuis les sources:

zope.component-3.10.0.tar.gz
zope.component-3.4.0.tar.gz
zope.deferredimport-3.4.0.tar.gz
zope.deprecation-3.4.0.tar.gz
zope.event-3.4.1.tar.gz
zope.exceptions-3.4.0.tar.gz
zope.interface-3.4.0.tar.gz
zope.testing-3.5.6.tar.gz

> python setup.py build
> sudo python setup.py install

Interfaces:
-----------
from zope.interface import Interface, Attribute
class IFoo(Interface):
     """Foo interface documentation"""

     x = Attribute("""Un attribut x""")
  
     def bar(q, r=None):
       """bar methode: arg: q, r=none"""

IFoo.__doc__
'Foo interface documentation'
IFoo.__name__
'IFoo'
IFoo.__module__
'__main__'

Note that `bar` doesn't take a `self` argument. When calling instance methods,
you don't pass a `self` argument, so a `self` argument isn't included in the
interface signature. 

names=list(IFoo)
names
['x', 'bar']

Declaring interfaces
====================

Having defined interfaces, we can *declare* that objects provide
them.  Before we describe the details, lets define some terms:

*provide*
   We say that objects *provide* interfaces.  If an object provides an
   interface, then the interface specifies the behavior of the
   object. In other words, interfaces specify the behavior of the
   objects that provide them.

*implement*
   We normally say that classes *implement* interfaces.  If a class
   implements an interface, then the instances of the class provide
   the interface.  Objects provide interfaces that their classes
   implement [#factory]_.  (Objects can provide interfaces directly,
   in addition to what their classes implement.)

   It is important to note that classes don't usually provide the
   interfaces that they implement.

   We can generalize this to factories.  For any callable object we
   can declare that it produces objects that provide some interfaces
   by saying that the factory implements the interfaces.

Now that we've defined these terms, we can talk about the API for
declaring interfaces.

Declaring implemented interfaces
--------------------------------

The most common way to declare interfaces is using the implements
function in a class statement::

from zope.interface import implements
class Foo:
    implements(IFoo)

    def __init__(self, x=None):
        self.x = x
  
    def bar(self, q, r=None):  
        return q, r, self.x
 
    def __repr__(self):
        return "Foo(%s)" % self.x


In this example, we declared that `Foo` implements `IFoo`. This means
that instances of `Foo` provide `IFoo`.  Having made this declaration,
there are several ways we can introspect the declarations.  First, we
can ask an interface whether it is implemented by a class::

  >>> IFoo.implementedBy(Foo)
  True

And we can ask whether an interface is provided by an object::

  >>> foo = Foo()
  >>> IFoo.providedBy(foo)
  True

Configuration march 2019:
+++++++++++++++++++++++++

Sous Windows, VSCode et Python 3.7.2
> pip3
Fatal error in launcher: Unable to create process using '"'
[ntird-us191-jg4:jgrelet]/c/git/python/pirata
> python3 -m pip install --upgrade pip
...
Successfully installed pip-19.0.3
[ntird-us191-jg4:jgrelet]/c/git/python/pirata

Sous Linux Ubuntu 16.04, l'upgrade de pip failed !
---------------------------------------------------
voir: https://askubuntu.com/questions/1025793/running-pip3-importerror-cannot-import-name-main
Utiliser:
> pip install <package> --user
ou 
> sudo pip install <package> 
ou
> python3 -m pip install --user <package>  # instead
ou
> sudo -H python3 -m pip install <package>

A tester:
Then I recommend adding the following aliases to your .bashrc:
pip() ( python -m pip "$@" )
pip3() ( python3 -m pip "$@" )

Commande pip pour lister les paquets installes, en root et mode user:
> pip list
> pip list --user
> pip show <package>

Behind a proxy:
> pip install guidata --proxy http://134.246.32.1:3128

Il est prefereable d'installer la derniere version Python 3.7.2

Configuration du fichier VSC setting.json de jgrelet:
-----------------------------------------------------

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
    "editor.formatOnPaste": true,

    // whitelist numpy to remove lint errors
    "python.linting.pylintArgs": [
        "--extension-pkg-whitelist=netCDF4"
    ]
Modules Python à intaller:
--------------------------

Autoformatting:
> pip install autopep8
Installer l'extension Python-autopep8
Cmd+P choisir autopip
> pip install pylint

Developpement:
> pip install toml
> pip install pynmea2
> pip install pySerial
> pip install netCDF4
> pip install netCDF4 
> pip install matplotlib
> pip install seawater
> pip install numpy
> pip install PyInstaller
> pip install PySimpleGUI
> pip install ConfigParser 
> pip install sip 
> pip install guidata 
> pip install Cython 
> pip install guiqwt (fail missing VC)
Download source from github
> python setup.py build -c mingw32 install

basemap
> sudo apt-get install libgeos-3.5.0 libgeos-c1v5 libgeos-dev
> sudo -H python3 -m pip install basemap-v1.1.0.tar.gz 

Installing collected packages: pyproj, pyshp, basemap
Successfully installed basemap-1.1.0 pyproj-2.1.2 pyshp-2.1.0

Pour utiliser QT au lieu de Tk
> pip install PySimpleGUIQt
> pip install PySide2
> pip install PyAstronomy
> pip install sciPy
> pip install basemap

Puis remplacer le :
import PySimpleGUI as gs
par
import PySimpleGUIQt as gs

Sous Ubuntu, installer python3-tk pour PySimpleGUI:
> sudo  apt-get install python3-tk

To create your EXE file from your program that uses PySimpleGUI, my_program.py, 
enter this command in your Windows command prompt:

> pyinstaller -wF my_program.py

Problem during execution (under Windows):
File "netCDF4\_netCDF4.pyx", line 1213, in init netCDF4._netCDF4
ModuleNotFoundError: No module named 'cftime'

Try solution may be found here:
https://stackoverflow.com/questions/29067588/problems-building-python-distribion-containing-netcdf4
Unistall/install last netCDF4 version:
> pip uninstall netCDF4
> pip install netCDF4

Edit and modify:
 C:\opt\python\Python37\Lib\site-packages\PyInstaller\hooks\hook-netCDF4.py
replace:
hiddenimports = ['netCDF4.utils', 'netcdftime']
with:
hiddenimports = ['netCDF4.utils', 'cftime']

Version [1.4.0](https://pypi.python.org/pypi/netCDF4/1.4.0) released. 
The netcdftime package is no longer included, it is now a separate 
[package](https://pypi.python.org/pypi/cftime) dependency. 

https://github.com/pyinstaller/pyinstaller/pull/4422/commits/a6098d062e713ab93d71ccb021d3c61f4a6b3360

Tests unitaires avec unittest:
--------------------
Configuration VSC, setting.json:
Modifier les arguments suivant l'application.

  "python.unitTest.unittestArgs": [
        "-v",
        "-s",
        "./tests",
        "-p",
        "test_*.py"
    ],
    "python.unitTest.pyTestEnabled": false,
    "python.unitTest.nosetestsEnabled": false,
    "python.unitTest.unittestEnabled": true,

Voir: https://docs.python.org/3.7/library/unittest.html?highlight=unittest

Les fichiers de tests sont sous tests
Run test in single file
> python - m unittest - v tests/test_roscop.py

Run all test_ * in dir tests:
> python -m unittest  discover tests -v
> python -m unittest  discover -s tests -p 'test_*.py' -v

Methods name:
assertEqual() 	
assertNotEqual() 
assertTrue() 	
assertFalse() 	
assertRaises() 	
assertAlmostEqual() 	
assertNotAlmostEqual() 	
assertRegex() 	  	
assertNotRegex() 	
assertRaisesRegex()

Git:
-------
Pour mettre à jour le depot distant après l'avoir créé sur github.com
> git pull origin master --allow-unrelated-histories
From https://github.com/jgrelet/oceano2python
 * branch            master     -> FETCH_HEAD
Merge made by the 'recursive' strategy.
 README.md | 2 ++
 1 file changed, 2 insertions(+)
 create mode 100644 README.md

make test
