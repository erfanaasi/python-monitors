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
    echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/python2-monitors"' >> ~/.bashrc
    echo 'export PYTHONPATH="${PYTHONPATH}:/path/to/python2-monitors/monitors/parser"' >> ~/.bashrc
```
4) For creating the parser files (same works for RegExp.g4):
```bash
    cd <clone-dir>/monitors/parser
    antlr4 -Dlanguage=Python2 PastMTL.g4
``` 
5) To test the installation:
```bash
    cd <clone-dir>/examples
    python example_mtl_1.py
``` 
