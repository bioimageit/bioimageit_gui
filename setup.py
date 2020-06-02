# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='bioimageapp',
    version='0.1.0',
    description='Gui application for bioimagepy',
    long_description=readme,
    author='Sylvain Prigent',
    author_email='sylvain.prigent@inria.fr',
    url='https://gitlab.inria.fr/serpico/bioimageapp',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        "pyside2"
    ],
    )
