import requests
import os
from datetime import datetime

def trigger_rollback(alert):
    if alert['status'] == 'firing':
        date_str = datetime.now().strftime('%Y-%m-%d')
        
        # Trigger Airflow DAG
        airflow_url = f"http://airflow-webserver:8080/api/v1/dags/rollback_pipeline/dagRuns"
        headers = {
            "Content-Type": "application/json",
            "Authorization": "Bearer " + os.getenv('AIRFLOW_API_TOKEN')
        }
        payload = {
            "conf": {
                "date": date_str
            }
        }
        
        response = requests.post(airflow_url, json=payload, headers=headers)
        response.raise_for_status()
        
        return {"status": "rollback triggered"}
    return {"status": "no action"}

if __name__ == "__main__":
    import json
    import sys
    
    alert = json.loads(sys.stdin.read())
    result = trigger_rollback(alert)
    print(json.dumps(result))