set PIPENV_DOTENV_LOCATION=.env.development
pipenv run flask db upgrade && pipenv run python setup_defaults.py