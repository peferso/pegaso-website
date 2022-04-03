pipeline {
    agent any
    environment {
        BINDIR = '/var/lib/jenkins/.local/bin'
        TFPROJECTREPO = 'https://github.com/.../terraform-demo.git'
    }
    stages {

        stage('Install pip in jenkins env') {
            steps {
               sh '''#!/bin/bash
                curl -O https://bootstrap.pypa.io/get-pip.py
                python3 get-pip.py --user
                '''
            }
        }
        stage('Activate environment') {
            steps {
                sh '''#!/bin/bash
                source bin/activate
                '''
            }
        }
        stage('Update packages') {
            steps {
                sh '''#!/bin/bash
                export PATH=${HOME}/.local/bin:${PATH#*:}
                '''
            }
        }
        stage('Update packages') {
            steps {
                sh '''#!/bin/bash
                /var/lib/jenkins/.local/bin/pip install -r requirements.txt
                '''
            }
        }
        stage('Website deployment configurations') {
            steps {
                sh '''#!/bin/bash
                cd src/pegaso_website
                replace_cmd=s/#HOST#/`curl -s ifconfig.co`/g
                sed -i "${replace_cmd}" settings.py
                cd ${OLDPWD}
                '''
            }
        }
    }
}
