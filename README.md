# ETL-Cloud
Le projet ETL-Cloud est une solution complète pour l'extraction, transformation et chargement de données dans un environnement cloud. L'architecture est conçue pour être scalable, fiable et facile à maintenir.

## Technologies utilisées
- ***Extract (E)***: Apache NiFi
- ***Transform (T)***: Apache Spark ou dbt (Data Build Tool) comme alternaitive 
- ***Load (L)***: PostgreSQL (dans un cloud public ou privé)
- ***Orchestration***: Apache Airflow
- ***Stockage intermédiaire***: MinIO (self-hosted)
- ***Monitoring et Logs***: Prometheus, Grafana, ELK (Elasticsearch, Logstash, Kibana)
- ***CI/CD et Automatisation***: GitHub Actions

## Architecture de la pipeline ETL
1. **Extraction des données (E - Extract)**
- Sources : API REST, bases de données relationnelles (PostgreSQL, MySQL), fichiers CSV, JSON, Parquet.
- Outil : Apache NiFi (Airbyte autre alternative) pour extraire les données et les charger dans un stockage temporaire.

2. **Stockage intermédiaire**
- Stockage brut des données extraites dans MinIO.
- Transformation des données (T - Transform)
- Nettoyage, normalisation et enrichissement avec Apache Spark.
- Stockage des résultats transformés dans un Data Warehouse (PostgreSQL).

3. **Chargement des données (L - Load)**
- Ingestion des données transformées dans le Data Warehouse.
- Partitionnement et indexation pour optimiser les performances.

4. **Orchestration & automatisation**
- Apache Airflow orchestre l’exécution des tâches ETL et gère les dépendances.
- Automatisation du déploiement avec GitHub Actions.

5. **Monitoring et observabilité**
- Prometheus & Grafana surveillent les performances et l’état des jobs ETL.
- ELK (Elasticsearch, Logstash, Kibana) pour la gestion des logs.

## Déploiement Cloud & Infrastructure
- ***Infrastructure as Code (IaC)***: Terraform / Ansible pour provisionner l’environnement cloud (OpenStack).
- ***Conteneurisation***: Docker & Kubernetes pour exécuter les jobs ETL de manière scalable.

## Pipeline CI/CD
- Linting & Tests des scripts SQL, OpenStack, Ansible et Terraform.
- Déploiement automatisé des tâches ETL via GitHub Actions.
- Rollback automatique en cas d’échec.


## Structure du projet ETL-Cloud
```bash
etl-cloud-project/
│── infrastructure/                # Provisioning Cloud & Kubernetes  
│   ├── terraform/                 # Infrastructure as Code (IaC)  
│   │   ├── main.tf                # Définition des ressources cloud  
│   │   ├── variables.tf           # Variables Terraform  
│   │   ├── outputs.tf             # Outputs Terraform  
│   │   └── providers.tf           # Configuration des providers (OpenStack ou Autres)  
│   ├── ansible/                   # Configuration des serveurs  
│   │   ├── playbook.yml           # Playbook Ansible pour configurer les instances  
│   │   └── inventory.ini          # Fichier d'inventaire des serveurs  
│── data_pipeline/                 # Code ETL  
│   ├── extract/                   # Extraction des données  
│   │   ├── nifi/                  # Flux Apache NiFi   
│   │   │   ├── extract_flow.xml   # Configuration du flux NiFi  
│   │   ├── airbyte/               # Configurations Airbyte (si utilisé) 
│   │   │   ├── source_config.json # Connexion aux sources de données  
│   │   │   ├── destination_config.json # Configuration du stockage  
│   ├── transform/                 # Transformation des données  
│   │   ├── dbt_project/           # Modèles de transformation avec dbt  (si utilisé)
│   │   │   ├── models/            # Modèles SQL  
│   │   │   ├── seeds/             # Données statiques pour enrichissement  
│   │   │   ├── dbt_project.yml    # Configuration du projet dbt  
│   │   ├── spark_jobs/            # Jobs Spark pour transformations avancées  
│   │   │   ├── clean_data.py      # Nettoyage des données  
│   │   │   ├── enrich_data.py     # Enrichissement des données  
│   │   │   ├── aggregate_data.py  # Agrégation des données  
│   ├── load/                      # Chargement des données  
│   │   ├── load_to_dwh.sql        # Requêtes d’insertion dans PostgreSQL  
│   │   ├── data_partitioning.py   # Gestion du partitionnement  
│   ├── orchestration/             # Orchestration ETL avec Airflow  
│   │   ├── dags/                  # DAGs Apache Airflow  
│   │   │   ├── etl_pipeline.py    # Définition du pipeline ETL complet  
│   │   ├── docker-compose.yml     # Déploiement local d’Airflow  
│── monitoring/                    # Surveillance et logs  
│   ├── prometheus/                # Configuration Prometheus  
│   │   ├── prometheus.yml         # Fichier de config  
│   ├── grafana/                   # Dashboards Grafana  
│   │   ├── dashboards.json        # Configurations des graphiques  
│   ├── elk/                       # Stack ELK pour logs  
│   │   ├── logstash.conf          # Pipeline Logstash
│── rollback/                      # Gestion des échecs et rollback  
│   ├── airflow/                   # Rollback au niveau de l'orchestration  
│   │   ├── rollback_dag.py        # DAG Airflow pour rollback en cas d’échec  
│   ├── database/                  # Rollback au niveau de la base de données  
│   │   ├── rollback_queries.sql    # Requêtes pour restaurer l’état précédent  
│   ├── storage/                   # Rollback des fichiers stockés  
│   │   ├── rollback_s3.py         # Restauration depuis MinIO  
│   │   ├── rollback_gcs.py        # Restauration depuis Google Cloud Storage  (si utilisé)
│   ├── monitoring/                # Détection des erreurs et rollback  
│   │   ├── alertmanager.yml       # Configuration d’Alertmanager pour rollback  
│   │   ├── rollback_notifier.py   # Script pour déclencher le rollback en cas d’alerte  
│── ci_cd/                         # Automatisation et CI/CD  
│   ├── github_actions/            # Workflows GitHub Actions  
│   │   ├── ci.yml                 # Linting et tests  
│   │   ├── cd.yml                 # Déploiement automatique
│   │   ├── rollback.yml           # Rollback automatique si échec du déploiement 
│── docs/                          # Documentation  
│   ├── architecture.md            # Description de l’architecture  
│   ├── installation.md            # Guide d’installation  
│   ├── usage.md                   # Guide d’utilisation  
│── .gitignore                     # Fichiers à ignorer  
│── README.md                      # Présentation du projet  
│── requirements.txt                # Dépendances Python  
│── Dockerfile                      # Conteneurisation  
│── docker-compose.yml               # Déploiement multi-services  
```
## Auteur 
- William BATCHAYON (@batchayw)

## Astus
Les variables d'environnement sont préconfigurées avec des valeurs par défaut mais peuvent être surchargées via un fichier `.env`.
