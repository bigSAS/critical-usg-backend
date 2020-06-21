:: run always before pytest tests
SET CUSG_SECRET=PYTEST-TOP-SECRET
SET CUSG_TESTING=YES
SET CUSG_DEBUG=NO
SET PGPASSWORD=postgres

C:
cd C:\Program Files\PostgreSQL\12\bin
psql -U postgres -a -f c:\sql\cusg_test_db.sql
D:
cd D:\critical-usg\critical-usg-backend
.env\Scripts\activate && flask db upgrade && python setup_defaults.py
