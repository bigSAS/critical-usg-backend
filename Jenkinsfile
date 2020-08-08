pipeline {
    agent {
        node {
            label 'vps-master'
        }
    }

    triggers {
        pollSCM('*/2 * * * *')
    }

    environment {
        CUSG_VERSION = '1.0.0'
        CUSG_DEBUG = 'YES'
        CUSG_ENV = 'dev'
        CUSG_PORT = '8088'
        CUSG_GUNICORN_WORKERS = '2'
        CUSG_SECRET = credentials('cusg-secret')
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
                build (
                    job: 'CUSG-TESTS',
                    parameters: [
                        string(name: 'CUSG_BRANCH', value: 'release/dev')
                    ]
                )
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
}
