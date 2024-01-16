pipeline {
    agent any

    stages {
        stage('Build and Push Image') {
            steps { 
                script {
                    // Set additional environment variable
                    withEnv(["HOME=${env.WORKSPACE}"]) {
                        // Build Docker image
                        sh 'docker build -t flaskapp .'

                        // Tag the Docker image
                        sh 'docker tag flaskapp ikechucool4real/flaskapp'

                        // Push the Docker image to Docker Hub
                        sh 'docker push ikechucool4real/flaskapp'
                    }                       
                }
            }
        }
            steps {
                script {
                    // Build Docker image
                    sh 'docker build -t flaskapp .'

                    // Tag the Docker image
                    sh 'docker tag flaskapp ikechucool4real/flaskapp'

                    // Push the Docker image to Docker Hub
                    sh 'docker push ikechucool4real/flaskapp'
                }
            }
        }

        stage('Stop and Remove Existing Container') {
            steps {
                script {
                    // Stop the existing Docker container (if running)
                    sh 'docker stop flaskapp || true'

                    // Remove the existing Docker container (if exists)
                    sh 'docker rm flaskapp || true'
                }
            }
        }

        stage('Run Docker Container') {
            steps {
                script {
                    // Run the Docker container
                    sh 'docker run -p 80:5000 -d --name flaskapp ikechucool4real/flaskapp'
                }
            }
        }
    }
}
