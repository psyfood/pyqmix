#!/usr/bin/env bash

# Fail script immediately on any errors in external commands,
# and display each line as it gets executed.
set -ev

echo "Installing Miniconda environment..."
wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
bash miniconda.sh -b -p $HOME/miniconda
export PATH="$HOME/miniconda/bin:$PATH"
hash -r
conda config --set always_yes yes --set changeps1 no
conda update -q conda
conda info -a
conda create -n pyqmix python=$PYTHON_VERSION
conda env list
