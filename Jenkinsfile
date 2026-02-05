pipeline {
    agent { label 'testing' }

    environment {
        APP_NAME = "library-management"
        VERSION_BASE = "1.0"
        VENV_DIR = ".venv"     
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
                set -euxo pipefail

                python3 -m venv .venv
                . .venv/bin/activate

                python -m pip install --upgrade pip
                pip install -r requirements.txt
                '''
            }
        }

        stage('Start Postgres (CI)') {
            steps {
                sh '''
                set -euxo pipefail

                # Start postgres container for tests
                docker rm -f ci-postgres || true
                docker run -d --name ci-postgres \
                    -e POSTGRES_DB=library_test \
                    -e POSTGRES_USER=postgres \
                    -e POSTGRES_PASSWORD=postgres \
                    -p 5432:5432 \
                    postgres:16

                # Wait until ready
                for i in $(seq 1 30); do
                    docker exec ci-postgres pg_isready -U postgres && break
                    sleep 1
                done
                '''
            }
            }

        stage('Test') {
            environment {
                DATABASE_URL = 'postgresql+psycopg2://postgres:postgres@localhost:5432/library_test'
                FLASK_ENV = 'testing'
            }
            steps {
                sh '''
                set -euxo pipefail
                . .venv/bin/activate
                pytest -q
                '''
            }
        }

        post {
            always {
                sh 'docker rm -f ci-postgres || true'
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