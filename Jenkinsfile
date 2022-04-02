pipeline {
    agent any
    environment {
        TFPROJECTFOLDER = 'terraform-demo'
        TFPROJECTREPO = 'https://github.com/.../terraform-demo.git'
    }
    stages {

        stage('Start website') {
            steps {
                sh '''#!/bin/bash
                source bin/activate
                '''
            }
            steps {
                sh '''#!/bin/bash
                pip install -r requirements.txt
                '''
            }
            steps {
                sh '''#!/bin/bash
                cd src
                python manage.py runserver
                '''
            }


        }
    }
}
