# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='bioimageit_gui',
    version="0.2.0",
    author="Sylvain Prigent and BioImageIT team",
    author_email="bioimageit@gmail.com",
    description='Gui application for BioImageIT',
    long_description=readme,
    url='https://github.com/bioimageit/bioimageit_gui',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "qtpy"
    ],
    )
