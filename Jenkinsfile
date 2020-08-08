pipeline {
  agent {
    node {
      label 'vps-master'
    }
  }

  triggers {
    pollSCM('*/5 * * * *')
  }

  stages {
    stage('Build docker image') {
      steps {
        sh 'docker-compose build cusg'
      }
    }

    stage('Test') {
      environment {
        CUSG_DEBUG = 'YES'
        CUSG_ENV = 'test'
        CUSG_SECRET = 'testing-secret'
        PSSWD_DB_COMMAND = "alter user postgres with password 'postgres'"
        CREATE_DB_COMMAND = "CREATE DATABASE cusg_db_test"
      }

      steps {
        node('cusg-server-tests-slave') {
            sh 'service postgresql start'
            sh 'psql -U postgres -c ${PSSWD_DB_COMMAND}'
            sh 'PGPASSWORD=postgres psql -c ${CREATE_DB_COMMAND} -U postgres'
            sh 'pip install -r req-dev.txt'
            sh 'python manage.py db upgrade'
            sh 'python -m pytest -v --log-cli-level=${LOG_LEVEL} tests/'
        }
      }
    }

    stage('Stop services') {
      steps {
        sh 'docker-compose stop'
      }
    }

    stage('Run services') {
      steps {
        sh 'docker-compose up -d'
      }
    }

  }
  environment {
    CUSG_VERSION = '1.0.0'
    CUSG_DEBUG = 'YES'
    CUSG_ENV = 'dev'
    CUSG_PORT = '8088'
    CUSG_GUNICORN_WORKERS = '2'
    CUSG_SECRET = credentials('cusg-secret')
  }
}
