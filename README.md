Python2 version of the Python-monitors package.

# How to run it:
1) Install package:
```
    git clone git@github.com:erfanaasi/python2-monitors.git
    cd <clone-dir>
    python setup.py install
```
2) Install ctx package:
```
    pip install ctx
```
3) Go to the parser folder:
```
    cd parser
```
4) To make the antlr files compatible with Python2, delete all the files, except "PastMTL.g4" and "RegExp.g4", and run:
```
    antlr4 -Dlanguage=Python2 PastMTL.g4
``` 
(Same works for RegExp.g4)

    
