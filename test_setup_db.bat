:: run always before pytest tests
del app_test.db
SET CUSG_SECRET=PYTEST-TOP-SECRET
SET CUSG_TESTING=YES
SET CUSG_DEBUG=NO
.env\Scripts\activate && flask db upgrade && python setup_defaults.py
