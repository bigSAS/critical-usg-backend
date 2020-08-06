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
        sh 'docker build -t $image_name .'
      }
    }

    stage('Stop + delete container') {
      steps {
        sh 'docker stop $container_name || true'
        sh 'docker rm $container_name || true'
      }
    }

    stage('Run app') {
      steps {
        sh '''docker run -d --name ${container_name} \\
-p ${expose_on_port}:80 \\
-e GUNICORN_WORKERS=${gunicorn_workers} \\
-e CUSG_SECRET=${secret} \\
-e ALLOWED_HOSTS="${allowed_hosts}" \\
-e CUSG_DB_CONNETION_STRING=${db_connection_string} \\
$image_name'''
      }
    }

  }
  environment {
    image_name = 'cusg-backend-dev:latest'
    gunicorn_workers = '3'
    expose_on_port = '8088'
    container_name = 'cusg-backend-dev'
    secret = credentials('cusg-secret')
    db_connection_string = credentials('cusg-db-connection-string')
    allowed_hosts = credentials('cusg-allowed-hosts')
  }
}