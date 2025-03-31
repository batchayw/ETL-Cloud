# Guide d'Utilisation

## Exécution du pipeline ETL

1. **Démarrer le pipeline manuellement**:
   - Accéder à l'interface Airflow: http://localhost:8080
   - Activer le DAG `etl_pipeline`
   - Déclencher une exécution manuelle

2. **Surveillance**:
   - Grafana: http://localhost:3000 (admin/admin)
   - Prometheus: http://localhost:9090
   - Kibana: http://localhost:5601

## Configuration des sources de données

Modifier les fichiers dans `data_pipeline/extract/`:

- `nifi/extract_flow.xml` pour les flux NiFi
- `airbyte/*.json` pour les connecteurs Airbyte

## Développement des transformations

1. **Transformations Spark**:
   - Modifier les scripts dans `data_pipeline/transform/spark_jobs/`
   - Tester avec:
     ```bash
     docker exec -it etl-cloud_spark_1 spark-submit /jobs/clean_data.py
     ```

2. **Transformations dbt**:
   ```bash
   cd data_pipeline/transform/dbt_project
   dbt run --models staging
   ```

## Gestion des erreurs

En cas d'échec:

1. Consulter les logs dans Airflow
2. Vérifier les alertes dans Alertmanager
3. Le rollback automatique se déclenche pour les erreurs critiques