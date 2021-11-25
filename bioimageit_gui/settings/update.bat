
set install_dir=%1
set conda_dir=%2

set conda_path="%conda_dir%\condabin\conda.bat"
call %conda_dir%\Scripts\activate.bat bioimageit

cd "%install_dir%\bioimageit_formats"
git pull
cd "%install_dir%\bioimageit_core"
git pull
cd "%install_dir%\bioimageit_gui"
git pull
cd "%install_dir%\bioimageit_viewer"
git pull


REM install and config packages
pip install "%install_dir%\bioimageit_formats"
pip install "%install_dir%\bioimageit_core"
pip install "%install_dir%\bioimageit_gui"
pip install "%install_dir%\bioimageit_viewer"
