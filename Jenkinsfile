pipeline {
  agent {
    node {
      label 'vps-master'
    }

  }
  stages {
    stage('Build docker image') {
      steps {
        sh 'docker build -t $image_name .'
      }
    }

  }
  environment {
    image_name = 'cusg-backend-dev:latest'
    gunicorn_workers = '3'
    expose_on_port = '8088'
  }
}