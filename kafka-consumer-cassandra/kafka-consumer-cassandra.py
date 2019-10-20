from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import DCAwareRoundRobinPolicy

import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark_cassandra

from predict_model import predict
from datetime import datetime

cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'

auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['cassandra'], port=9042, auth_provider=auth_provider)

# cluster = Cluster(contact_points=['cassandra'])
session = cluster.connect()
# session = cluster.connect(cassandra_keyspace)

# session.execute("create keyspace inappropriate_language_detection with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};")
#
session.execute('use inappropriate_language_detection;')
#
# session.execute("create table if not exists inappropriate_tweets (tweet text, username text, prediction int, date text, country text, primary key (tweet));")


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


def main():
    # Create Spark Context to Connect Spark Cluster
    sc = SparkContext()
    sc.setLogLevel("ERROR")

    # Set the Batch duration to 10 sec of Streaming Context
    ssc = StreamingContext(sc, 10)

    # Create Kafka Stream to Consume Data Comes From Twitter Topic
    # localhost:2181 = Default Zookeeper Consumer Address
    kafkaStream = KafkaUtils.createStream(ssc, 'zookeeper:2181', 'spark-streaming', {'twitter': 1})

    # Count the number of offensive tweets per user
    user_offensive_tweets = kafkaStream \
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

    # Start Execution of Streams
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()
