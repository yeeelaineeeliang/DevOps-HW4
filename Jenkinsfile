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
                script {
                    def sha = readFile('.gitsha').trim()
                    def artifactName = "${APP_NAME}-${env.BRANCH_NAME}-${env.BUILD_NUMBER}-${sha}.zip"
                    sh """
                      rm -rf dist
                      mkdir -p dist
                      zip -r "dist/${artifactName}" app database requirements.txt Dockerfile docker-compose.yml Jenkinsfile README.md pytest.ini sonar-project.properties || true
                    """
                    echo "Created artifact: dist/${artifactName}"
                }
            }
        }

        stage('Archive Artifact') {
            steps {
                archiveArtifacts artifacts: 'dist/*.zip', fingerprint: true
            }
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
