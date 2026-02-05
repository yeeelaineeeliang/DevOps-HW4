pipeline {
    agent { label 'testing' }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                echo "Building on branch: ${env.BRANCH_NAME}"
            }
        }

        stage('Test') {
            steps {
                sh 'pytest'
            }
        }

        stage('Deploy') {
            when {
                branch 'main'
            }
            steps {
                echo 'Deploying application (main branch only)'
            }
        }
    }

    post {
        always {
            echo 'Pipeline finished'
        }
    }
}
