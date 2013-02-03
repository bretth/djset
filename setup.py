#!/usr/bin/env python
import distribute_setup
distribute_setup.use_setuptools()
from setuptools import setup


setup(name='djset',
    version='0.1',
    description="Utilities for Django settings secrets",
    author='Brett Haydon',
    url='https://github.com/bretth/djset',
    packages=['djset'],
    license='LICENSE.txt',
    entry_points={"console_scripts":
    ["djs_locate_settings = djset.djset:locate_settings",
     "djset = djset.command:main",
     ]},
    scripts=['dexportunset.sh',],
    install_requires = ["keyring"],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2 :: Only',
        'Topic :: Software Development',
    ]
)