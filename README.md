# Friends-Library

## to execute one file with test:
python -m unittest tests.test_ksiazka

## to execute all tests we need to be in the project main directory Friends-Library, and then:
python -u "tests\run_tests.py"

## to check compliance with pep8:
pycodestyle src/operacje.py

## to make changes into the file:
autopep8 --in-place --aggressive --aggressive --max-line-length=79 src/operacje.py  