
script_update_mac =   '#!/bin/bash'\
                      'installdir=$1'\
                      'conda_dir=$2'\
                      'conda_bin="$conda_dir/condabin/conda"'\
                      'conda_sh="$installdir/miniconda3/etc/profile.d/conda.sh"'\
                      'python_path="$installdir/miniconda3/envs/bioimageit/bin/python"'\
                      'pip_path="$installdir/miniconda3/envs/bioimageit/bin/pip"'\
                      'cd $installdir/bioimageit_formats'\
                      'git pull'\
                      'cd $installdir/bioimageit_core'\
                      'git pull'\
                      'cd $installdir/bioimageit_gui'\
                      'git pull'\
                      'cd $installdir/bioimageit_viewer'\
                      'git pull'\
                      '$pip_path install ./bioimageit_formats'\
                      '$pip_path install ./bioimageit_core'\
                      '$pip_path install ./bioimageit_gui'\
                      '$pip_path install ./bioimageit_viewer"'
