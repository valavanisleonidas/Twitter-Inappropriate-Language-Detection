from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

import json

from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, TopicAndPartition
import pyspark_cassandra

from predict_model import predict
from datetime import datetime

cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'

auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['cassandra'], port=9042, auth_provider=auth_provider)

session = cluster.connect(cassandra_keyspace)

conf = SparkConf() \
    .setAppName("PySparkCassandra") \
    .set("spark.cassandra.connection.host", "cassandra") \
    .set("spark.cassandra.auth.username", "cassandra") \
    .set("spark.cassandra.auth.password", "cassandra")

checkpoints_folder = "checkpoints"


def filter_tweets_have_user(json_tweet):
    # print(json_tweet)

    if 'user' in json_tweet and 'screen_name' in json_tweet['user']:
        return True
    return False


def filter_tweets_only_english(json_tweet):
    lang = json_tweet['lang']
    if lang == 'en':
        return True
    return False


def filter_has_location_info(json_tweet):
    if json_tweet['place'] is not None \
            and 'country' in json_tweet['place'] \
            and json_tweet['place']['country'] is not None:
        # print(json_tweet)
        return True
    return False


# classes : 0-hateful, 1-offensive, and 2-clean
def filter_tweets_only_offensive(json_tweet):
    prediction = predict_tweet(json_tweet)

    if prediction == 1:
        # print('===========BEGIN TWEET ===================')
        # print(json_tweet["text"], '  prediction : ', prediction)
        # print('===========END TWEET===================')
        return True
    return False


def predict_tweet(json_tweet):
    text = json_tweet["text"]
    prediction = predict([text])
    return prediction


def create_transformations(kafka_stream):
    # Count the number of offensive tweets per user
    user_offensive_tweets = kafka_stream \
        .map(lambda value: json.loads(value[1])) \
        .filter(filter_tweets_have_user) \
        .filter(filter_tweets_only_english) \
        .filter(filter_tweets_only_offensive) \
        .filter(filter_has_location_info) \
        .map(lambda json_tweet: {
            'tweet': json_tweet['text'],
            'country': json_tweet['place']['country'],
            'date': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'prediction': int(predict_tweet(json_tweet)),
            'username': json_tweet["user"]["screen_name"]
        })

    user_offensive_tweets.pprint()

    user_offensive_tweets.foreachRDD(lambda x: x.saveToCassandra(cassandra_keyspace, cassandra_table))


def setup():
    sc = SparkContext(conf=conf)

    # Set the Batch duration to 10 sec of Streaming Context
    ssc = StreamingContext(sc, 10)
    ssc.sparkContext.setLogLevel("ERROR")
    ssc.checkpoint(checkpoints_folder)

    kafka_params = {"metadata.broker.list": "kafka:9092",
                    "zookeeper.connect": "zookeeper:2181",
                    "group.id": "spark-streaming",
                    "zookeeper.connection.timeout.ms": "10000",
                    "auto.offset.reset": "smallest"}
    start = 0
    partition = 0
    topic = 'twitter'
    topic_partition = TopicAndPartition(topic, partition)
    from_offset = {topic_partition: int(start)}

    # Create Kafka Stream to Consume Data Comes From Twitter Topic
    # localhost:2181 = Default Zookeeper Consumer Address
    kafka_stream = KafkaUtils.createDirectStream(ssc, [topic], kafka_params, fromOffsets=from_offset)

    create_transformations(kafka_stream)

    return ssc


def main():
    # Create Spark Context to Connect Spark Cluster
    ssc = StreamingContext.getOrCreate(checkpoints_folder, setup)
    ssc.sparkContext.setLogLevel("ERROR")

    # Start Execution of Streams
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()
