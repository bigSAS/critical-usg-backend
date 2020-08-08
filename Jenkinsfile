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
      steps {
        node('cusg-server-tests-slave') {
            CUSG_DEBUG = 'YES'
            CUSG_ENV = 'test'
            CUSG_SECRET = 'wordddd'
            PGPASSWORD = 'postgres'
            sh '''psql -U postgres -c "alter user postgres with password '${PGPASSWORD}'"'''
            sh 'psql -c "CREATE DATABASE cusg_db_${CUSG_ENV}" -U postgres'
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
