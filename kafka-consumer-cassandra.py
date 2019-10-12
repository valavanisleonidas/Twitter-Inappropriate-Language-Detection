
from kafka.consumer import KafkaConsumer

from cassandra.cluster import Cluster

import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import pyspark_cassandra
from predict_model import predict


cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'

cluster = Cluster()
session = cluster.connect(cassandra_keyspace)




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
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:2181', 'spark-streaming', {'twitter': 1})

    # Count the number of offensive tweets per user
    user_offensive_tweets = kafkaStream \
        .map(lambda value: json.loads(value[1])) \
        .filter(filter_tweets_have_user) \
        .filter(filter_tweets_only_english) \
        .filter(filter_tweets_only_offensive) \
        .map(lambda json_object: (json_object["user"]["screen_name"], 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .transform(lambda rdd: rdd.sortBy(lambda x: x[1], ascending=False))

    user_offensive_tweets.pprint()

    user_offensive_tweets.foreachRDD(lambda x: x.saveToCassandra(cassandra_keyspace, cassandra_table))


    # Start Execution of Streams
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()
