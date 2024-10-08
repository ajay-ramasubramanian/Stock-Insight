import io
import os
import sys
import json
import pandas as pd
import s3fs
from minio import Minio

class MinioRetriever:
    def __init__(self, user, topic, container, host) -> None:
        self.container = container #raw
        self.user = user
        self.topic = str(topic).replace("_","-")
        self.host = host


    def retrieve_object(self,key=None):
        try:
            # Set up S3 filesystem (MinIO uses S3 protocol)
            fs = s3fs.S3FileSystem(
                endpoint_url=f"http://{self.host}:9000",
                key="minioadmin",
                secret="minioadmin"
            )
            # print(f"topic:{self.topic}")

            # List all objects in the specified subfolder
            if not key:
                paths = [
                    self.container,
                    f"{self.container}/{self.topic}",
                    f"{self.container}/{self.topic}/{self.user}",
                    f"{self.container}/{self.topic}/{self.user}/{self.container}-{self.topic}.parquet"
                ]
                
                for path in paths:
                    print("True" if fs.exists(path) else "False")

                # Construct the path to the parquet file
                parquet_path = f"{self.topic}/{self.user}/{self.container}-{self.topic}.parquet"

                df = self.read_object(parquet_path, self.container)
            else:
                str(key).replace("_","-")
                paths = [
                    self.container,
                    f"{self.container}/{self.topic}",
                    f"{self.container}/{self.topic}/{self.user}",
                    f"{self.container}/{self.topic}/{self.user}/{self.container}-{key}.parquet"
                ]
                
                for path in paths:
                    print("True" if fs.exists(path) else "False")

                # Construct the path to the parquet file
                parquet_path = f"{self.topic}/{self.user}/{self.container}-{key}.parquet"

                df = self.read_object(parquet_path, self.container)

            
            return df

        except Exception as e:
            print(f"Error in retrieve_and_convert_to_dataframe function: {e}")
            return None
        
    def read_object(self, prefix, bucket):
        try:
            client = Minio(
            f"{self.host}:9000",
            access_key="minioadmin",
            secret_key="minioadmin",
            secure=False  # Set to True if using HTTPS
            )

            data = client.get_object(bucket, prefix)

            with io.BytesIO(data.read()) as parquet_buffer:
                df = pd.read_parquet(parquet_buffer)

            return df

        except Exception as e:
            print(f"Error in read_object function: {e}")  # More detailed error message
            return None

class MinioUploader:
    def __init__(self, user, topic, container,host) -> None:
        self.container = container
        self.user = user
        self.topic = str(topic).replace("_","-")
        self.host = host


    def ensure_bucket_exists(self, client, bucket_name):
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        else:
            print(f"Bucket '{bucket_name}' already exists")


    def upload_files(self, data, key=None):
            minio_client = Minio(
                f"{self.host}:9000", 
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False  # Keep this False for localhost without HTTPS
            )
            fs = s3fs.S3FileSystem(
                    key="minioadmin",
                    secret="minioadmin",
                    endpoint_url=f"http://{self.host}:9000",  # Explicitly set the endpoint URL
                    client_kwargs={'endpoint_url': f"http://{self.host}:9000"},
                    use_ssl=False  # Set to False for localhost without HTTPS
                )
            bucket_name = f'{self.container}'
            self.ensure_bucket_exists(minio_client,bucket_name)
            if not key:
                path = f"{self.container}/{self.topic}/{self.user}/{self.container}-{self.topic}.parquet"
                try:
                    with fs.open(path, 'wb') as f:
                        data.to_parquet(f, engine='pyarrow', compression='snappy')
                except Exception as e:
                    print(f"\nError occured while uploading file to bucket : {e}")
            else:
                key=str(key).replace("_","-")
                print(key)
                path = f"{self.container}/{self.topic}/{self.user}/{self.container}-{key}.parquet"
                try:
                    with fs.open(path, 'wb') as f:
                        data.to_parquet(f, engine='pyarrow', compression='snappy')
                    print("Uploaded file sucessfully !!")
                except Exception as e:
                    print(f"\nError occured while uploading file to bucket : {e}")

            
        

