pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                echo 'Stage 1: Building Docker containers...'
                sh 'docker --version'
            }
        }

        stage('E2E Tests') {
            steps {
                echo 'Stage 2: Running Playwright E2E tests...'
            }
        }

        stage('Performance Tests') {
            steps {
                echo 'Stage 3: Running Locust performance tests...'
            }
        }

        stage('Report') {
            steps {
                echo 'Stage 4: Publishing test reports...'
            }
        }
    }
}