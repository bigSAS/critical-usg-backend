export CUSG_DEBUG=YES
export CUSG_SECRET=SECRET
export CUSG_ENV=TEST

sudo docker exec postgres psql -U postgres -c "DROP DATABASE cusg_db_test"
sudo docker exec postgres psql -U postgres -c "CREATE DATABASE cusg_db_test"

python manage.py db upgrade && \
python -m pytest \
  -vrf --log-cli-level=ERROR \
  --log-file=tests_runner.log \
  tests/