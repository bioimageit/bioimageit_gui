Introduction
============

BioImageApp is a desktop graphical user interface for the BioImagePy library

Context
-------
BioImageApp has been developped by **Sylvain Prigent** in a project funded by `France-BioImaging <https://france-bioimaging.org/>`_
BioImageApp is the desktop graphical interface for the project. Please find all the other developped tools `here <https://gitlab.inria.fr/bioimage-it/>`_

BioImageApp
-----------
BioImageApp is a python3 Qt application. It provides a graphical user interface for scientific experiment data management, analysis and visualisation.
It is made of three components:

* **Browser**: the browser application allows to navigate through the database of data, visualise data and anotate data
* **Tool finder**: the finder application is a graphical interface to navigate the data processing tools and their documentation orginized into toolboxes.  
* **Tool runner**: the runner application is a graphical interface to execute processed on data. Data can be processed individualy, by batch from a directory and by batch from an anotated experiment dataset  