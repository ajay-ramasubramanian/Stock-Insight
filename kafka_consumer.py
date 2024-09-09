import json
from producers.utils import schemas, TOPICS
import avro.schema
from avro.io import DatumReader
import io
import pandas as pd
from kafka import KafkaConsumer, KafkaProducer

# from spotify_user_data_extraction import users_saved_tracks


def avro_deserializer(avro_bytes, schema):
    reader = DatumReader(schema)
    bytes_reader = io.BytesIO(avro_bytes)
    decoder = avro.io.BinaryDecoder(bytes_reader)
    return reader.read(decoder)

def process_dataframe(df, topic_name, partition, offset):

        print("Received DataFrame:")
        print("writing the file to a CSV file")
        df.to_csv(f"{topic_name}_{partition}_{offset}.csv", index = False)
        print("------------------------")
    

def consumer(bootstrap_servers=['localhost:9093'], 
               group_id='spotify_consumer_group'):
    
    # Create a Kafka consumer
    kafka_consumer = KafkaConsumer(
        bootstrap_servers=bootstrap_servers,
        auto_offset_reset='earliest',
        enable_auto_commit=True,
        group_id=group_id,
    )

    kafka_consumer.subscribe(TOPICS.values())
    print("Started Consumer")

# Avro deserializer

    try:
        # Try to parse the message as JSON
        while True:
            message = kafka_consumer.poll(timeout_ms=1000)
            if message:
                # print(f"data: {data}")
                print(f"message type: {type(message)}")
                print(f"message: {message}")
                # topic, user = message.topic, message.key
                # data = avro_deserializer(message.value, schemas["spotify_"+str(topic)])
                print("------------------------------------------------------------------------------------------------------------------------------------")
                # topic_name, partition, offset = message.topic, message.partition, message.offset
                # data = json.loads(message.value)
                # # Convert the message value (list of dicts) back to a DataFrame
                # df = pd.DataFrame(data)
                # # Process the DataFrame
                # process_dataframe(df, topic_name, partition, offset)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        print(f"Problematic message: {message.value[:100]}...")  # Print first 100 chars of the message
    except Exception as e:
        print(f"Error processing message: {e}")

    except KeyboardInterrupt:
        print("Consumer stopped")

    finally:
        # Close the consumer
        kafka_consumer.close()

# Run consumer
consumer()