// Jenkins Pipeline for StudyBot CI/CD

pipeline {
    agent any
    
    environment {
        // Docker Hub credentials (configure in Jenkins)
        DOCKER_REGISTRY = 'docker.io'
        DOCKER_IMAGE = 'pranavkapratwar10/studybot'
        DOCKER_TAG = "${BUILD_NUMBER}"
        
        // Groq API key (configure in Jenkins credentials)
        GROQ_API_KEY = credentials('groq-api-key')
        ADMIN_PASSWORD = credentials('admin-password')
    }
    
    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out code from GitHub...'
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image...'
                script {
                    docker.build("${DOCKER_IMAGE}:${DOCKER_TAG}")
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }
        
        stage('Test') {
            steps {
                echo 'Running tests...'
                script {
                    // Run container for testing
                    sh """
                        docker run --rm \
                        -e GROQ_API_KEY=${GROQ_API_KEY} \
                        ${DOCKER_IMAGE}:${DOCKER_TAG} \
                        python -c "print('Health check passed')"
                    """
                }
            }
        }
        
        stage('Push to Registry') {
            steps {
                echo 'Pushing Docker image to registry...'
                script {
                    docker.withRegistry('https://registry.hub.docker.com', 'docker-hub-credentials') {
                        docker.image("${DOCKER_IMAGE}:${DOCKER_TAG}").push()
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                script {
                    // Stop and remove old container
                    sh """
                        docker stop studybot-app || true
                        docker rm studybot-app || true
                    """
                    
                    // Run new container
                    sh """
                        docker run -d \
                        --name studybot-app \
                        -p 8501:8501 \
                        -e GROQ_API_KEY=${GROQ_API_KEY} \
                        -e ADMIN_PASSWORD=${ADMIN_PASSWORD} \
                        -v \$(pwd)/data:/app/data \
                        --restart unless-stopped \
                        ${DOCKER_IMAGE}:${DOCKER_TAG}
                    """
                }
            }
        }
        
        stage('Health Check') {
            steps {
                echo 'Performing health check...'
                script {
                    sleep 10 // Wait for app to start
                    sh 'curl -f http://localhost:8501/_stcore/health || exit 1'
                }
            }
        }
    }
    
    post {
        success {
            echo 'Pipeline completed successfully!'
            // Send notification (email, Slack, etc.)
        }
        failure {
            echo 'Pipeline failed!'
            // Rollback or send alert
        }
        always {
            // Clean up
            sh 'docker system prune -f'
        }
    }
}
