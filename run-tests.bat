set CUSG_SECRET=secret
set CUSG_ENV=test
set CUSG_DEBUG=YES

:: run always before pytest tests
docker exec postgres-local psql -U postgres -c "DROP DATABASE cusg_db_test"
docker exec postgres-local psql -U postgres -c "CREATE DATABASE cusg_db_test"

pipenv run python manage.py db upgrade && ^
pipenv run python -m pytest ^
  -vrf --log-cli-level=ERROR ^
  --log-file=tests_runner.log ^
  tests/
