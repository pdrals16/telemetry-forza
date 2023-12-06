import boto3
import logging

from botocore.exceptions import ClientError

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

class BucketManager():
    def __init__(self) -> None:
        pass
    
    @property
    def s3_client(self):
        return boto3.client("s3")
    
    def put_object(self, bucket_name, data, path):
        try: 
            logging.info(f"Putting data into bucket {bucket_name}/{path}")
            self.s3_client.put_object( 
                Bucket=bucket_name,
                Body=data,
                Key=path
            )
        except ClientError as e:
            return False
        return True

class DataWriter():
    def __init__(self, path: str) -> None:
        self.path = path
        pass

    def insert(self, data):
        with open(self.path, 'a') as _file:
            _file.write(data)
        return None