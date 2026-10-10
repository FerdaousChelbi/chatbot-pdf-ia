pipeline {
    agent any

    stages {
        stage('Checkout GIT') {
            steps {
                echo 'Pulling...'
                git branch: 'main',
                    url: 'https://github.com/FerdaousChelbi/chatbot-pdf-ia.git'
            }
        }
        stage('Afficher la date') {
            steps {
                sh 'date'
            }
        }
    }
}
