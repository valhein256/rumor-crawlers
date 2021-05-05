pipeline {

    agent {
        label 'slave && ubuntu && ap-northeast-1'
    }

    environment {
        EMAIL_TO = ''
        SERVICE = 'rumor-crawlers'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '24'))
        disableConcurrentBuilds()
        ansiColor('xterm')
        timestamps ()
        /*office365ConnectorWebhooks([[name: "Office 365",*/
                                     /*url: "<webhook_url>",*/
                                     /*startNotification: false,*/
                                     /*notifySuccess: false,*/
                                     /*notifyAborted: false,*/
                                     /*notifyUnstable: true,*/
                                     /*notifyFailure: true,*/
                                     /*notifyBackToNormal: true,*/
                                     /*notifyRepeatedFailure: false*/
        /*]])*/
    }

    triggers {
        cron('0 * * * *')
    }

    stages {
        stage('identify stage') {
            steps {
                script {
                    env.STAGE = [
                        'origin/master': 'dev',
                        'origin/beta': 'beta',
                        'origin/production': 'prod',
                    ].get(env.GIT_BRANCH, 'master')
                    env.TAG_IMAGE = "${env.SERVICE}:${env.STAGE}"
                    env.DATE = sh(returnStdout: true, script: 'date +"%d"').trim().toInteger()
                    env.HOUR = sh(returnStdout: true, script: 'date +"%H"').trim().toInteger()
                    env.IMAGE_NOT_EXIST = sh (script: "sudo docker images -q ${env.TAG_IMAGE}", returnStdout: true).trim().isEmpty()
                }
                sh "printenv"
            }
        }

        stage("Get Repo") {
            steps {
                git branch: 'master',
                    credentialsId: '',
                    url: ''
            }
        }

        stage("build develop") {
            when { 
                anyOf {
                    changeset "Dockerfile"
                    changeset "pyproject.toml"
                    changeset "poetry.lock"
                    changeset "Jenkinsfile*"
                    environment name: 'IMAGE_NOT_EXIST', value: 'true'
                    allOf {
                        environment name: 'DATE', value: "1"
                        environment name: 'HOUR', value: "13"
                    }
                }
            }
            steps {
                sh '''
                    set +x
                    sudo docker build --pull . \
                    -t ${TAG_IMAGE}
                '''
            }
        }

        stage("Run job") {
            steps {
                script {
                    sh '''
                        make config stage=${STAGE}

                        sudo docker run \
                        -v ${PWD}:/opt/app \
                        -v /var/log/rumor-crawlers:/var/log/rumor-crawlers \
                        --rm ${TAG_IMAGE} \
                        python app/tfc.py 

                        sudo docker run \
                        -v ${PWD}:/opt/app \
                        -v /var/log/rumor-crawlers:/var/log/rumor-crawlers \
                        --rm ${TAG_IMAGE} \
                        python app/mygopen.py 
                    '''
                }
            }
        }
    }

    post {
        failure {
            emailext body: 'Check console output at $BUILD_URL to view the results. \n\n ${CHANGES} \n\n -------------------------------------------------- \n${BUILD_LOG, maxLines=100, escapeHtml=false}',
                     to: "${EMAIL_TO}",
                     subject: 'Build failed in Jenkins: $PROJECT_NAME - #$BUILD_NUMBER'
        }
        unstable {
            emailext body: 'Check console output at $BUILD_URL to view the results. \n\n ${CHANGES} \n\n -------------------------------------------------- \n${BUILD_LOG, maxLines=100, escapeHtml=false}',
                     to: "${EMAIL_TO}",
                     subject: 'Unstable build in Jenkins: $PROJECT_NAME - #$BUILD_NUMBER'
        }
        changed {
            emailext body: 'Check console output at $BUILD_URL to view the results.',
                     to: "${EMAIL_TO}",
                     subject: 'Jenkins build is back to normal: $PROJECT_NAME - #$BUILD_NUMBER'
        }
        cleanup{
            sh "cd <path> && sudo find . -name '*.pyc' -delete"
            deleteDir()
        }
    }
}
