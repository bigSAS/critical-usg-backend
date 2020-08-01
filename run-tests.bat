:: run always before pytest tests
docker exec postgre psql -U postgres -c "DROP DATABASE cusg_db_testing"
docker exec postgre psql -U postgres -c "CREATE DATABASE cusg_db_testing"

set PIPENV_DOTENV_LOCATION=.env.testing
pipenv run flask db upgrade && pipenv run python setup_defaults.py && pipenv run pytest -v
