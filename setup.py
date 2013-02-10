#!/usr/bin/env python
import distribute_setup
import sys
distribute_setup.use_setuptools()
from setuptools import setup


INSTALL_REQUIRES = ["keyring", "docopt"]
if sys.version_info[0] < 3: # Install the backport of configparser
    INSTALL_REQUIRES.append("configparser")
    

setup(name='djset',
    version='0.2',
    description="Utilities for Django settings secrets",
    author='Brett Haydon',
    author_email='brett@haydon.id.au',
    url='https://github.com/bretth/djset',
    packages=['djset'],
    py_modules=['distribute_setup'],
    license='LICENSE.txt',
    entry_points={"console_scripts":
    ["djs_locate_settings = djset.utils:locate_settings",
     "djsecret = djset.commands:djsecret",
     "djconfig = djset.commands:djconfig",
     ]},
    scripts=['dexportunset.sh',],
    install_requires = INSTALL_REQUIRES,
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development',
    ]
)