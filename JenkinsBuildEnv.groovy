/*
Prepare building environment for Jenkinsfile pipeline
*/
def version = '1.0.0' // todo: read version from code
def devPort = '8088'
def prdPort = '9001'


def CUSG_ENV = env.BRANCH_NAME == 'release/dev' ? 'dev' : 'prod'
def CUSG_DEBUG = env.BRANCH_NAME == 'release/dev' ? 'YES' : 'NO'
def CUSG_VERSION = env.BRANCH_NAME == 'release/dev' ? version + '-dev' : version
def CUSG_PORT = env.BRANCH_NAME == 'release/dev' ? devPort : prdPort
def CUSG_SECRET = env.BRANCH_NAME == 'release/dev' ? 'not-so-seret' : credentials('cusg-secret')

return [
    CUSG_ENV: CUSG_ENV,
    CUSG_DEBUG: CUSG_DEBUG,
    CUSG_VERSION: CUSG_VERSION,
    CUSG_PORT: CUSG_PORT,
    CUSG_SECRET: CUSG_SECRET
]
