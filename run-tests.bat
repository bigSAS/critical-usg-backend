:: run always before pytest tests
docker exec postgre psql -U postgres -c "DROP DATABASE cusg_db_test"
docker exec postgre psql -U postgres -c "CREATE DATABASE cusg_db_test"

set PIPENV_DOTENV_LOCATION=.env.testing && ^
pipenv run python manage.py db upgrade && ^
pipenv run python -m pytest ^
  -vrf --log-cli-level=ERROR ^
  --log-file=tests_runner.log ^
  tests/
