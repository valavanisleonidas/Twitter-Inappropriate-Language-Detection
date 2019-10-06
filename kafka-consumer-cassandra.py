from cassandra.cqlengine import columns
from cassandra.cqlengine.models import Model
from kafka.consumer import KafkaConsumer

from cassandra.cluster import Cluster
import json

from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'

cluster = Cluster()
session = cluster.connect(cassandra_keyspace)


class InappropriateTweet(Model):
    id = columns.UUID(primary_key=True)
    tweet = columns.Text()
    prediction = columns.Integer


def tweet_contains_user(json_tweet):
    if 'user' in json_tweet and 'screen_name' in json_tweet['user']:
        return True
    return False


def main():
    # Create Spark Context to Connect Spark Cluster
    sc = SparkContext()
    sc.setLogLevel("ERROR")

    # Set the Batch duration to 10 sec of Streaming Context
    ssc = StreamingContext(sc, 10)

    # Create Kafka Stream to Consume Data Comes From Twitter Topic
    # localhost:2181 = Default Zookeeper Consumer Address
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:2181', 'spark-streaming', {'twitter': 1})

    # Count the number of tweets per User
    user_counts = kafkaStream \
        .map(lambda value: json.loads(value[1])) \
        .filter(tweet_contains_user) \
        .map(lambda x: {x["user"]["screen_name"], 1}) \
        .reduceByKey(lambda x, y: x + y) \
        .map(lambda x: {'tweet': x[0], 'prediction': x[1]})

    user_counts.pprint()

    # user_counts.foreachRDD(lambda x: InappropriateTweet.create(tweet="asdas", prediction=1).save())
    # user_counts.saveToCassandra(cassandra_keyspace, cassandra_table)
    # user_counts.foreachRDD(lambda x: x.saveToCassandra(cassandra_keyspace, cassandra_table))

    # df = spark.createDataFrame(user_counts)
    # df.write \
    #     .format("org.apache.spark.sql.cassandra") \
    #     .mode('append') \
    #     .options(table="kv", keyspace="test") \
    #     .save()

    # Start Execution of Streams
    ssc.start()
    ssc.awaitTermination()


def insert_tweet_to_db(json_tweet):
    # print(json_tweet)
    if not tweet_contains_user(json_tweet):
        return None
    # print(json_tweet["user"]["screen_name"])
    user_insert_stmt = session.prepare("insert into inappropriate_tweets (tweet, prediction) values (?,?)")
    return session.execute(user_insert_stmt, [json_tweet["user"]["screen_name"], 1])


def main2():
    print("creating consumer")
    consumer = KafkaConsumer(kafka_topic,
                             auto_offset_reset='earliest',
                             enable_auto_commit=True,
                             bootstrap_servers=['localhost:9092'],
                             api_version=(0, 10),
                             consumer_timeout_ms=1000,
                             value_deserializer=lambda x: json.loads(x.decode('utf-8')))
    
    print("inserting to db")
    for tweet in consumer:
        insert_tweet_to_db(tweet.value)


if __name__ == "__main__":
    main()
    # main2()
