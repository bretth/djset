#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup


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
    ["djs_locate_settings = djset.djset:locate_settings",
     "djsecret = djset.commands:djsecret",
     "djconfig = djset.commands:djconfig",
     ]},
    scripts=['dexportunset.sh',],
    install_requires = ["keyring", "docopt"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development',
    ]
)