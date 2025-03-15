cd /mnt/c/Users/Azeral/Documents/Sorbonne/M2/DAAR/TME_webAPI_base_20250227/TME_webAPI_DAAR/mySearchEngine &&
source ../../myTidyVEnv/bin/activate &&
python3 manage.py refreshOnSaleList >> ~/mySearchEngineLog &&
python3 manage.py refreshAvailableList >> ~/mySearchEngineLog &&
python3 manage.py refreshImageAssociations >> ~/mySearchEngineLog &&
python3 manage.py refreshGutenbergImages >> ~/mySearchEngineLog &&
deactivate
