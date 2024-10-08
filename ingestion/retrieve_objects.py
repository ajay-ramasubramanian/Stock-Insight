import site
import sys

sys.path.extend(site.getsitepackages())
import io
import json
import os

import pandas as pd
import s3fs
from dotenv import load_dotenv
from minio import Minio

load_dotenv(override=True)


class MinioRetriever:
    def __init__(self, user, topic, container) -> None:
        self.ret_container = container #raw
        self.user = user
        self.topic = topic.replace("_","-")
        
    def retrieve_object(self):
        try:
            # Set up S3 filesystem (MinIO uses S3 protocol)
            fs = s3fs.S3FileSystem(
                endpoint_url=f"http://{os.getenv('HOST')}:9000",
                key="minioadmin",
                secret="minioadmin",
                client_kwargs={
                    'endpoint_url': f"http://{os.getenv('HOST')}:9000"
    }
                
            )

            print(self.topic)

            print(os.getenv('HOST'))
            # List all objects in the specified subfolder
            if fs.exists(f"{self.ret_container}"):
                print(f"Folder Path :{self.ret_container} exists")
            else:
                print(f"Folder Path :{self.ret_container} does not exists")

            if fs.exists(f"{self.ret_container}/{self.topic}"):
                print(f" Folder Path: {self.ret_container}/{self.topic} exists")
            else:
                print(f" Folder Path: {self.ret_container}/{self.topic} exists")

            if fs.exists(f"{self.ret_container}/{self.topic}/{self.user}"):
                print(f" Folder Path: {self.ret_container}/{self.topic}/{self.user} exists")
            else:
                print(f"Folder Path : {self.ret_container}/{self.topic}/{self.user} does not exists")

            object_list = fs.ls(f"{self.ret_container}/{self.topic}/{self.user}")
            # Initialize an empty list to store all JSON data
            all_data = []

            # Iterate through each object and read its content
            for obj in object_list:
                with fs.open(obj, 'r') as f:
                    json_data = json.load(f)
                    for record in json_data: # unpacking batched data if any
                        all_data.append(record)
            return all_data
            
            # print(f"Successfully retrieved and converted {len(all_data[0])} objects from {self.topic}/{self.user}")
            # # return df

        except Exception as e:
            print(f"Error in retrieve_and_convert_to_dataframe function: {e}")
            return None


class MinioUploader:
    def __init__(self, user, topic, container) -> None:
        self.container = container
        self.user = user
        self.topic = topic.replace("_","-")


    def ensure_bucket_exists(self, client, bucket_name):
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"Bucket '{bucket_name}' created successfully")
        else:
            print(f"Bucket '{bucket_name}' already exists")


    def upload_files(self,data):
            minio_client = Minio(
                f"{os.environ.get('HOST')}:9000",
                access_key="minioadmin",
                secret_key="minioadmin",
                secure=False  # Keep this False for localhost without HTTPS
            )
            fs = s3fs.S3FileSystem(
                    key="minioadmin",
                    secret="minioadmin",
                    endpoint_url=f"http://{os.getenv('HOST')}:9000",  # Explicitly set the endpoint URL
                    client_kwargs={'endpoint_url': f"http://{os.getenv('HOST')}:9000"},
                    use_ssl=False  # Set to False for localhost without HTTPS
                )

            bucket_name = f'{self.container}'
            self.ensure_bucket_exists(minio_client,bucket_name)
            path = f"{self.container}/{self.topic}/{self.user}/{self.container}-{self.topic}.parquet"
            try:
                with fs.open(path, 'wb') as f:
                    data.to_parquet(f, engine='pyarrow', compression='snappy')
            except Exception as e:
                print(f"\nError occured while uploading file to bucket : {e}")
            
        
        