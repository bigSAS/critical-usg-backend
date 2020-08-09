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
    environment {
        CUSG_VERSION = getVersion(env.BRANCH_NAME)
        CUSG_DEBUG = getDebug(env.BRANCH_NAME)
        CUSG_ENV = getEnv(env.BRANCH_NAME)
        CUSG_PORT = getPort(env.BRANCH_NAME)
        CUSG_GUNICORN_WORKERS = '2'
        CUSG_SECRET = getSecret(env.BRANCH_NAME)
    }
}

def version() { '1.0.0' }
def devPort() { '8088' }
def prdPort() { '9001' }
def secret() { credentials('cusg-secret') }

def getEnv(branch) {
    return branch == 'release/dev' ? 'dev' : 'prod'
}

def getDebug(branch) {
    return branch == 'release/dev' ? 'YES' : 'NO'
}

def getVersion(branch) {
    return branch == 'release/dev' ? version() + '-dev' : version()
}

def getPort(branch) {
    return branch == 'release/dev' ? devPort() : prdPort()
}

def getSecret(branch) {
    return branch == 'release/dev' ? 'not-so-seret' : secret()
}