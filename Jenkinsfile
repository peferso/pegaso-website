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

                source ../bin/activate

                python manage.py runserver

                '''
            }
        }
    }
}
