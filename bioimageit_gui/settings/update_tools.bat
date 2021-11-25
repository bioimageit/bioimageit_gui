

set installdir=%1
set conda_dir=%2

set conda_path="%conda_dir%\condabin\conda.bat"
call %conda_dir%\Scripts\activate.bat bioimageit

cd "%installdir%\bioimageit-toolboxes"
git pull

copy "$installdir\bioimageit-toolboxes\thumbs\" "$installdir\toolboxes\thumbs\"
copy "$installdir\bioimageit-toolboxes\toolboxes.json" "$installdir\toolboxes\toolboxes.json"
copy "$installdir\bioimageit-toolboxes\tools.json" "$installdir\toolboxes\tools.json"
copy "$installdir\bioimageit-toolboxes\formats.json" "$installdir\formats.json"
