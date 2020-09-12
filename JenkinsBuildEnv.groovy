/*
Prepare building environment for Jenkinsfile pipeline
*/
def version = '1.0.0' // todo: read version from code
def port    = '9001'

def isProdBranch() { return env.BRANCH_NAME == 'release/prod' }

def CUSG_VERSION = version
def CUSG_PORT    = port
def CUSG_ENV     = isProdBranch() ? 'prod' : 'dev'
def CUSG_SECRET  = isProdBranch() ? credentials('cusg-secret') : 'notsosecret'
def FLASK_ENV    = isProdBranch() ? 'production' : 'development'
def FLASK_DEBUG  = isProdBranch() ? '0' : '1'

return [
    CUSG_ENV: CUSG_ENV,
    CUSG_VERSION: CUSG_VERSION,
    CUSG_PORT: CUSG_PORT,
    CUSG_SECRET: CUSG_SECRET,
    FLASK_ENV: FLASK_ENV,
    FLASK_DEBUG: FLASK_DEBUG
]
