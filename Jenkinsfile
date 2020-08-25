def buildEnv

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
                    buildEnv = load('JenkinsBuildEnv.groovy')
                    echo "${buildEnv}"
                }
            }
        }

        stage('Build docker image') {
            steps {
                script {
                    withEnv(["CUSG_VERSION=${buildEnv['CUSG_VERSION']}"]) {
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
                script {
                    withEnv([
                        "CUSG_ENV=${buildEnv['CUSG_ENV']}",
                        "CUSG_VERSION=${buildEnv['CUSG_VERSION']}",
                        "CUSG_PORT=${buildEnv['CUSG_PORT']}",
                        "CUSG_SECRET=${buildEnv['CUSG_SECRET']}",
                        "CUSG_DEBUG=${buildEnv['CUSG_DEBUG']}",
                        "CUSG_GUNICORN_WORKERS=2"
                    ]) {
                        sh 'docker-compose up -d'
                    }
                }
            }
        }
    }
}
