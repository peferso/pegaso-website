pipeline {
    agent any
    environment {
        TFPROJECTFOLDER = 'terraform-demo'
        TFPROJECTREPO = 'https://github.com/.../terraform-demo.git'
    }
    stages {

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
                pip install -r requirements.txt
                '''
            }
        }
        stage('Start website') {
            steps {
                sh '''#!/bin/bash
                cd src
                python manage.py runserver
                '''
            }
        }
    }
}
