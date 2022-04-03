pipeline {
    agent any
    environment {
        BINDIR = '/var/lib/jenkins/.local/bin'
        DBUSER = 'ec2-dbuser'
        DBHOST = ''
        SRCDIR = '/home/ec2-user/pegaso-website'
    }
    stages {
        stage('Adapt path to environment') {
            steps {
                sh '''#!/bin/bash
                echo -e "\n# Adapting PATH in Jenkins deployment\n" >> bin/activate
                echo "export PATH=${HOME}/.local/bin:${PATH#*:}" >> bin/activate
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
