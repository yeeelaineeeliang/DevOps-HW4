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

         stage('Install Dependencies') {
            steps {
                sh '''
                    # Use system Python (no venv needed for CI)
                    python3 -m pip install --user --upgrade pip
                    python3 -m pip install --user -r requirements.txt
                    python3 -m pip install --user pytest
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                . .venv/bin/activate
                pytest -q
                '''
            }
        }


        stage('Package Artifact') {
            steps {
                script {
                    def sha = readFile('.gitsha').trim()
                    def safeBranch = env.BRANCH_NAME.replaceAll('/', '-')
                    def artifactName = "${APP_NAME}-${safeBranch}-${env.BUILD_NUMBER}-${sha}.tar.gz"

                    sh """
                        rm -rf dist
                        mkdir -p dist
                        tar -czf "dist/${artifactName}" \
                            app \
                            database \
                            requirements.txt \
                            Dockerfile \
                            docker-compose.yml \
                            Jenkinsfile \
                            README.md \
                            pytest.ini \
                            sonar-project.properties
                    """

                    echo "Created artifact: dist/${artifactName}"
                }
            }
        }

        stage('Archive Artifact') {
            steps {
                archiveArtifacts artifacts: 'dist/*.tar.gz', followSymlinks: false
                echo "Artifact archived in Jenkins"
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