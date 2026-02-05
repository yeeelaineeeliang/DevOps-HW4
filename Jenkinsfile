pipeline {
    agent { label 'testing' }

    environment {
        APP_NAME = "library-management"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git rev-parse --short HEAD > .gitsha'
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

        stage('Package Artifact') {
            steps {
                sh '''
                rm -rf dist
                mkdir -p dist
                zip -r dist/library-management-${BRANCH_NAME}-${BUILD_NUMBER}.zip app database requirements.txt Jenkinsfile README.md
                '''
            }
        }

        stage('Archive Artifact') {
            steps {
                archiveArtifacts artifacts: 'dist/*.zip', followSymlinks: false
            }

        stage('Deploy') {
            when { branch 'main' }
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
