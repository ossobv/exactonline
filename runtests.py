from unittest import main
from warnings import simplefilter

simplefilter('default')  # needed on py2 to see DeprecationWarnings
main(module=None, argv=[
    'runtests.py', 'discover', '-v', '-t', '.', '-s', 'exactonline',
    '-p', '*_test.py'])
