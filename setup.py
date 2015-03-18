#!/usr/bin/env python
from distutils.core import setup

try:
    # PyPI prefers the readme as .txt
    with open('README.txt') as file:
        long_description = file.read()
except IOError:
    # We prefer it as .rst
    with open('README.rst') as file:
        long_description = file.read()


setup(
    name='exactonline',
    version='0.1.1',
    packages=['exactonline', 'exactonline.api'],
    data_files=[('', ['LICENSE.txt', 'README.rst'])],
    description='Exact Online REST API Library in Python',
    long_description=long_description,
    author='Walter Doekes',
    author_email='wjdoekes@osso.nl',
    url='https://github.com/ossobv/exactonline',
    license='LGPLv3+',
    platforms=['linux'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        ('License :: OSI Approved :: GNU Lesser General Public License v3 '
         'or later (LGPLv3+)'),
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Topic :: Office/Business :: Financial',
        'Topic :: Office/Business :: Financial :: Accounting',
        'Topic :: Software Development :: Libraries',
    ],
)

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
