SET CUSG_TESTING=YES
SET CUSG_DEBUG=NO
flask db upgrade
python -m pytest -v
SET CUSG_TESTING=NO
