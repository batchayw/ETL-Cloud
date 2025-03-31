# Guide d'Installation

## Prérequis
- Docker 20.10+
- Docker Compose 1.29+
- Python 3.9+
- Terraform 1.3+ (pour le déploiement cloud)

## Installation locale

1. **Cloner le dépôt**:
    ```bash
    git clone https://github.com/batchayw/etl-cloud.git
    cd etl-cloud
    ```

2. **Configurer l'environnement**:
    ```bash
    cp .env.example .env
    ```

3. **Démarrer les services**:
    ```bash
    docker-compose up -d
    ```

4. **Initialiser Airflow**:
    ```bash
    docker exec -it etl-cloud_airflow-webserver_1 airflow db init
    docker exec -it etl-cloud_airflow-webserver_1 airflow users create \
        --username admin \
        --password admin \
        --firstname Admin \
        --lastname User \
        --role Admin \
        --email admin@william.com
    ```

## Déploiement Cloud

1. **Configurer Terraform**:
    ```bash
    cd infrastructure/terraform
    cp terraform.tfvars.example terraform.tfvars
    # Modifier les valeurs dans terraform.tfvars
    ```

2. **Déployer l'infrastructure**:
    ```bash
    terraform init
    terraform plan
    terraform apply
    ```

3. **Configurer Ansible**:
    ```bash
    cd ../ansible
    ansible-playbook -i inventory.ini playbook.yml
    ```