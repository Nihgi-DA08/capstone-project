/*
Tóm tắt: pipeline build Docker image cho Dash app, push lên Docker Hub,
dọn container cũ và chạy lại container portugal-hotel-booking trên network yan.
*/
pipeline {
    agent any
    
    stages {
        // Build image mới từ Dockerfile trong repo.
        stage('Build') {
            steps {
                sh 'docker build -t yamiannephilim/dash:latest .'
            }
        }

        // Push image lên Docker Hub bằng credential Jenkins đã cấu hình.
        stage('Push') {
            steps {
                withDockerRegistry(credentialsId: 'docker_hub', url: 'https://index.docker.io/v1/') {
                    sh 'docker push yamiannephilim/dash'
                }
            }
        }

        // Dọn container cũ nếu còn tồn tại trước khi deploy bản mới.
        stage('Clean') {
            steps {
                script {
                    def containerName = sh(returnStdout: true, script: 'docker ps -aqf "name=portugal-hotel-booking"').trim()
                    if (containerName) {
                        sh "docker stop $containerName"
                        sh "docker rm $containerName"
                    }
                }
            }
        }

        // Chạy container mới với restart policy để app tự khởi động lại khi lỗi hoặc reboot.
        stage('Run') {
            steps {
                sh 'docker container stop portugal-hotel-booking || echo "this container does not exist"'
                sh 'docker network create yan || echo "this network exist"'
                sh 'echo y | docker container prune'
                sh 'docker run --name portugal-hotel-booking --network yan --restart=unless-stopped -p 8050:8050 -d yamiannephilim/dash:latest'
            }
        }
    }

    post {
        // Xóa workspace sau pipeline để tránh reuse artifact cũ.
        always {
            cleanWs()
        }
    }
}
