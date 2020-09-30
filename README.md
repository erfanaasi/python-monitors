Python2 version of the Python-monitors package.

# How to run it:
1) Install package:
```bash
    git clone git@github.com:erfanaasi/python2-monitors.git
    cd <clone-dir>
    python setup.py install
```
2) Install required packages:
```bash
    pip install ctx
    mkdir -p lib
    cd lib
    wget 'https://www.antlr.org/download/antlr-4.7.1-complete.jar'
    pip install antlr4-python2-runtime==4.7.1
```
3) For permanent settings use:

```bash
cd <clone-dir>
echo "export CLASSPATH=\".:$PWD/lib/antlr-4.7.1-complete.jar:$CLASSPATH\"" >> ~/.bashrc
echo "alias antlr4=\"java -jar $PWD/lib/antlr-4.7.1-complete.jar -visitor\"" >> ~/.bashrc
echo "alias grun=\"java org.antlr.v4.gui.TestRig\"" >> ~/.bashrc
```
4) Go to the parser folder:
```
    cd parser
```
5) To make the antlr files compatible with Python2, delete all the files, except "PastMTL.g4" and "RegExp.g4", and run:
```
    antlr4 -Dlanguage=Python2 PastMTL.g4
``` 
(Same works for RegExp.g4)

    
