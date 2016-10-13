#!/usr/bin/env python
from distutils.core import setup

if __name__ == '__main__':
    long_descriptions = []
    with open('README.rst') as file:
        long_descriptions.append(file.read())
    with open('CHANGES.rst') as file:
        long_descriptions.append(file.read())

    setup(
        name='exactonline',
        version='0.2.4',
        packages=['exactonline', 'exactonline.api', 'exactonline.elements'],
        data_files=[('', ['LICENSE.txt', 'README.rst', 'CHANGES.rst'])],
        description='Exact Online REST API Library in Python',
        long_description=('\n\n\n'.join(long_descriptions)),
        author='Walter Doekes, OSSO B.V.',
        author_email='wjdoekes+exactonline@osso.nl',
        url='https://github.com/ossobv/exactonline',
        license='LGPLv3+',
        platforms=['linux'],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            ('License :: OSI Approved :: GNU Lesser General Public License v3 '
             'or later (LGPLv3+)'),
            'Operating System :: POSIX :: Linux',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Topic :: Office/Business :: Financial',
            'Topic :: Office/Business :: Financial :: Accounting',
            'Topic :: Software Development :: Libraries',
        ],
    )

# vim: set ts=8 sw=4 sts=4 et ai tw=79:
