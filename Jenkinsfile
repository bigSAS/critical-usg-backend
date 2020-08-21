def g

pipeline {
    agent {
        node {
            label 'vps-master'
        }
    }

    triggers {
        pollSCM('*/2 * * * *')
    }

    stages {

        stage('Init') {
            steps {
                script {
                    g = load('jenkins.groovy')
                }
            }
        }

        stage('Build docker image') {
            steps {
                script {
                    withEnv([
                        "CUSG_ENV=${g.CUSG_ENV}",
                        "CUSG_VERSION=${g.CUSG_VERSION}",
                        "CUSG_PORT=${g.CUSG_PORT}",
                        "CUSG_SECRET=${g.CUSG_SECRET}",
                        "CUSG_DEBUG=${g.CUSG_DEBUG}",
                        "CUSG_GUNICORN_WORKERS=2"
                    ]) {
                        sh 'docker-compose build cusg'
                    }
                }
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
                        string(name: 'CUSG_BRANCH', value: env.BRANCH_NAME)
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
