#!/bin/bash

installdir=$1
conda_dir=$2

conda_bin="$conda_dir/condabin/conda"
conda_sh="$conda_dir/etc/profile.d/conda.sh"
python_path="$installdir/miniconda3/envs/bioimageit/bin/python"
pip_path="$conda_dir/envs/bioimageit/bin/pip"


echo $installdir
echo $conda_dir

cd $installdir/bioimageit_formats
git pull
cd $installdir/bioimageit_core
git pull
cd $installdir/bioimageit_gui
git pull
cd $installdir/bioimageit_viewer
git pull


# install and config packages
$pip_path install $installdir/bioimageit_formats
$pip_path install $installdir/bioimageit_core
$pip_path install $installdir/bioimageit_gui
$pip_path install $installdir/bioimageit_viewer
