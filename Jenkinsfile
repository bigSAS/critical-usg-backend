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
      }

      steps {
        node('cusg-server-tests-slave') {

            sh 'PGPASSWORD=postgres service postgresql start && psql -U postgres -c "create database cusg_db_test;"'
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
