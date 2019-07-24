# BioImageApp

BioImageApp is a GUI application for BioImagePy.
BioImageApp is part of the BioImageIT project

# Install

BioImageApp depends and BioImagePy and needs a BioImageIT toolshed.
The following instructions shows how to deploy the BioImageIT. It is the 
recommended installation especially for devs. Nevertheless, one can install
the packages with *pip* and use the any directories organisation since the 
coonfiguration file `config/config.json` allows to specify each directory 
location.

## Root directory

Create the root directory:

```
mkdir bioimageit
cd bioimageit
```

## Install bioimagepy

BioImagePy is the core of the application. Use the following commands to install
it:

```
git clone git@gitlab.inria.fr:serpico/bioimagepy.git
```

## Install the toolshed

The toolshed is a directory containing all the data processing tools. A toolshed
can be very specific depending on which tools are installable on the system, 
which tools are needed...

In this example, we install the basic toolshed from the Serpico repository.
See the `serpico-toolshed` repository for more configuration details.

```
git clone git@gitlab.inria.fr:serpico/serpico-toolshed.git
cd serpico-toolshed
chmod u+x package.sh
./package.sh
cd ..
rm -rf serpico-toolshed
```

## Install BioImageApp

```
git clone git@gitlab.inria.fr:serpico/bioimageapp.git
```

Finally you shoud get the following directories architecture
- bioimageit
  - bioimageapp
  - bioimagepy
  - toolshed
  
Run the application:

```
python3 bioimageapp/app.py
```

# Configuration 

If you used the derictory architecture descibed above, the `config/config.json` 



