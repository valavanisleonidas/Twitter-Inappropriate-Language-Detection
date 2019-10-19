from pyspark import SparkContext
from pyspark.sql import SparkSession
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils, TopicAndPartition
from predict_model import predict

import json

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
        .map(lambda json_object: (json_object["user"]["screen_name"], 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .transform(lambda rdd: rdd.sortBy(lambda x: x[1], ascending=False))

    # .map(lambda json_object: (json_object["text"], 1))
    # .map(lambda json_object: (json_object["user"]["screen_name"], 1))

    # Print the User and the predictions
    user_offensive_tweets.pprint()


def setup():
    sc = SparkContext(appName="PythonStreamingTweets")
    # sc.setLogLevel("ERROR")

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
