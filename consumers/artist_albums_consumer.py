from kafka import KafkaConsumer
from base_consumer import BaseKafkaConsumer
from utils import TOPIC_CONFIG

class ArtistAlbumsConsumer(BaseKafkaConsumer):
    
    KAFKA_BOOTSTRAP_SERVERS = ['localhost:9093']
    TOPIC = TOPIC_CONFIG['artist_albums']['topic']

    def __init__(self, group_id):
        super().__init__('spotify_artist_albums')
        self.consumer = KafkaConsumer(
            bootstrap_servers = ArtistAlbumsConsumer.KAFKA_BOOTSTRAP_SERVERS,
            auto_offset_reset = 'earliest',  # Start reading from the earliest message available
            group_id = group_id,  # Assign consumer to a group for offset management
        )
        # Subscribe to the specified topic
        self.consumer.subscribe([ArtistAlbumsConsumer.TOPIC])

if __name__ == '__main__':
    artist_albums = ArtistAlbumsConsumer('artist_albums_group')
    artist_albums.consume(artist_albums.consumer)
