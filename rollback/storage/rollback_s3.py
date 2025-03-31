import boto3 # type: ignore
from datetime import datetime, timedelta

def rollback_minio(bucket_name, date_str):
    s3 = boto3.client(
        's3',
        endpoint_url='http://minio:9000',
        aws_access_key_id='AKIAIOSFODNN7EXAMPLE',
        aws_secret_access_key='wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'
    )

    # Delete files from the failed run
    objects = s3.list_objects_v2(Bucket=bucket_name, Prefix=date_str)
    if 'Contents' in objects:
        s3.delete_objects(
            Bucket=bucket_name,
            Delete={'Objects': [{'Key': obj['Key']} for obj in objects['Contents']]}
        )

    # Restore previous version
    prev_date = (datetime.strptime(date_str, '%Y-%m-%d') - timedelta(days=1)).strftime('%Y-%m-%d')
    prev_objects = s3.list_objects_v2(Bucket=f"{bucket_name}-backup", Prefix=prev_date)
    
    if 'Contents' in prev_objects:
        for obj in prev_objects['Contents']:
            copy_source = {'Bucket': f"{bucket_name}-backup", 'Key': obj['Key']}
            s3.copy_object(
                Bucket=bucket_name,
                Key=obj['Key'],
                CopySource=copy_source
            )

if __name__ == "__main__":
    import sys
    rollback_minio(sys.argv[1], sys.argv[2])