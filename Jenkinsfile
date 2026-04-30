// Jenkinsfile
// =============================================================================
// CI/CD Pipeline — LearnHub Testing Pipeline
// =============================================================================
// This pipeline automates the full test lifecycle:
//   1. Build   → Build all Docker containers (app + test runner)
//   2. E2E     → Run Playwright tests against the live Wagtail app
//   3. Perf    → Run Locust performance tests against the 3 APIs
//   4. Report  → Publish all test reports as Jenkins build artifacts
//
// Architecture: docker-compose.test.yml orchestrates 3 services (db, web, tests).
// The test container connects to the app via http://web:8000 on Docker's
// internal network. Jenkins uses 'docker compose exec' to run commands
// inside the already-running test container.
// =============================================================================

pipeline {
    agent any

    environment {
        COMPOSE_FILE = 'docker-compose.test.yml'
        COMPOSE_PROJECT_NAME = "learnhub-${BUILD_NUMBER}"
    }

    stages {

        // ---------------------------------------------------------------------
        // Stage 1: Build
        // ---------------------------------------------------------------------
        // Builds all Docker images and starts the services.
        // If requirements.txt has errors or a Dockerfile is broken, it fails here.
        // depends_on + healthchecks ensure the app is ready before tests run.
        // ---------------------------------------------------------------------
        stage('Build') {
            steps {
                sh 'docker compose build'
                sh 'docker compose up -d'
                // Wait for the web healthcheck to pass
                sh '''
                    echo "Waiting for Wagtail to be ready..."
                    timeout 120 sh -c '
                        until docker compose ps web | grep -q "healthy"; do
                            sleep 3
                            echo "Still waiting..."
                        done
                    '
                    echo "Wagtail is ready!"
                '''
            }
        }

        // ---------------------------------------------------------------------
        // Stage 2: E2E Tests (Playwright)
        // ---------------------------------------------------------------------
        // Runs all Playwright test files via pytest inside the test container.
        // pytest-playwright integrates Playwright with pytest's discovery,
        // fixtures, and reporting system.
        // --html generates the HTML report with screenshots on failure.
        // Tests run against http://web:8000 (Docker internal network).
        // Continue on failure — we want the report even if tests fail.
        // ---------------------------------------------------------------------
        stage('E2E Tests') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        docker compose exec -T tests \
                            pytest tests/e2e/ \
                            --browser chromium \
                            --base-url http://web:8000 \
                            --html=/app/test-results/playwright/report.html \
                            --self-contained-html \
                            -v
                    '''
                }
            }
        }

        // ---------------------------------------------------------------------
        // Stage 3: Performance Tests (Locust)
        // ---------------------------------------------------------------------
        // Runs Locust in headless mode against the 3 APIs.
        // --headless: no web UI, just run and produce results.
        // --html: generates the HTML report with charts.
        // --csv: exports raw data for further analysis.
        // Tests each API with ?mode=slow and without for comparison.
        // Continue on failure — we want metrics regardless.
        // ---------------------------------------------------------------------
        stage('Performance Tests') {
            steps {
                catchError(buildResult: 'UNSTABLE', stageResult: 'FAILURE') {
                    sh '''
                        docker compose exec -T tests \
                            locust \
                            -f tests/performance/locustfile.py \
                            --host=http://web:8000 \
                            --headless \
                            -u 50 -r 10 \
                            --run-time 60s \
                            --html=/app/test-results/locust/report.html \
                            --csv=/app/test-results/locust/results
                    '''
                }
            }
        }

        // ---------------------------------------------------------------------
        // Stage 4: Report
        // ---------------------------------------------------------------------
        // Always runs, even if previous stages failed.
        // Archives all test reports as Jenkins build artifacts.
        // After clicking a build number in Jenkins, reports are downloadable.
        // ---------------------------------------------------------------------
        stage('Report') {
            steps {
                // Archive Playwright HTML report
                archiveArtifacts artifacts: 'test-results/playwright/**/*',
                    allowEmptyArchive: true

                // Archive Locust HTML report + CSV data
                archiveArtifacts artifacts: 'test-results/locust/**/*',
                    allowEmptyArchive: true

                // Publish Playwright HTML report (if HTML Publisher plugin installed)
                publishHTML(target: [
                    reportName: 'Playwright Report',
                    reportDir: 'test-results/playwright',
                    reportFiles: 'report.html',
                    keepAll: true,
                    alwaysLinkToLastBuild: true,
                    allowMissing: true
                ])
            }
        }
    }

    post {
        always {
            // Tear down all containers and volumes — clean slate for next build.
            // Each build uses a unique COMPOSE_PROJECT_NAME (includes BUILD_NUMBER)
            // so parallel builds don't interfere with each other.
            sh 'docker compose down -v --remove-orphans || true'
        }
    }
}