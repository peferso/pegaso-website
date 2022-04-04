pipeline {
    agent any
    environment {
        BINDIR = '/var/lib/jenkins/.local/bin'
        SRCDIR = '/home/ec2-user/pegaso-website'
        DBUSER = '\$DBUSER_AWS'
        DBHOST = '\$DBHOST_AWS'
        DBPASS = '\$DBPASS_AWS'
        APIPRT = '\$APIPRT_AWS'
        APIEPT = '\$APIEPT_AWS'
    }
    stages {
        stage('Adapt path to environment') {
            steps {
                sh '''#!/bin/bash
                echo -e "\n# Adapting PATH and environment variables in Jenkins deployment\n" >> bin/activate
                echo "export PATH=${HOME}/.local/bin:${PATH#*:}" >> bin/activate
                echo "export DBHOST=${DBHOST}" >> bin/activate
                echo "export DBPASS=${DBPASS}" >> bin/activate
                echo "export DBUSER=${DBUSER}" >> bin/activate
                echo "export RF_API_PORT=${APIPRT}" >> bin/activate
                echo "export RF_API_ENDPOINT=${APIEPT}" >> bin/activate
                '''
            }
        }
        stage('Website deployment configurations') {
            steps {
                sh '''#!/bin/bash
                cd src/pegaso_website
                replace_cmd=s/#HOST#/*/g
                sed -i "${replace_cmd}" settings.py
                cd ${OLDPWD}
                '''
            }
        }
        stage('Move source code') {
            steps {
               sh '''#!/bin/bash
                sudo su ec2-user -c "rsync -azhv --chmod=ugo+r --chmod=ugo+w --chmod=ugo+x ./* ${SRCDIR} --delete"
               '''
            }
        }
    }
}
