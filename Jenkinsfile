// Simplified Jenkins Pipeline for StudyBot - Local Build Only

pipeline {
    agent any
    
    environment {
        DOCKER_IMAGE = 'studybot'
        BUILD_TAG = "${BUILD_NUMBER}"
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo '✅ Code checked out from GitHub'
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo '🐳 Building Docker image...'
                script {
                    bat "docker build -t ${DOCKER_IMAGE}:${BUILD_TAG} ."
                    bat "docker build -t ${DOCKER_IMAGE}:latest ."
                }
            }
        }
        
        stage('Test Image') {
            steps {
                echo '🧪 Testing Docker image...'
                script {
                    bat "docker run --rm ${DOCKER_IMAGE}:${BUILD_TAG} python --version"
                }
            }
        }
        
        stage('Tag for Render') {
            steps {
                echo '🏷️ Image ready for deployment!'
                script {
                    bat "docker images ${DOCKER_IMAGE}"
                }
            }
        }
    }
    
    post {
        success {
            echo '✅ Pipeline completed successfully!'
            echo '📦 Docker image built: ' + env.DOCKER_IMAGE + ':' + env.BUILD_TAG
            echo '🚀 Ready to deploy to Render!'
        }
        failure {
            echo '❌ Pipeline failed!'
        }
        always {
            echo '🧹 Cleaning up...'
        }
    }
}
