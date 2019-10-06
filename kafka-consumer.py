
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils
import json


def filter_tweets(json_tweet):
    # print(json_tweet)
    if 'user' in json_tweet and 'screen_name' in json_tweet['user']:
        return True
    return False


def main():
    # Create Spark Context to Connect Spark Cluster
    sc = SparkContext(appName="PythonStreamingTweets")
    sc.setLogLevel("ERROR")

    # Set the Batch duration to 10 sec of Streaming Context
    ssc = StreamingContext(sc, 10)

    # Create Kafka Stream to Consume Data Comes From Twitter Topic
    # localhost:2181 = Default Zookeeper Consumer Address
    kafkaStream = KafkaUtils.createStream(ssc, 'localhost:2181', 'spark-streaming', {'twitter': 1})

    # Count the number of tweets per User
    user_counts = kafkaStream \
        .map(lambda value: json.loads(value[1])) \
        .filter(filter_tweets) \
        .map(lambda json_object: (json_object["user"]["screen_name"], 1)) \
        .reduceByKey(lambda x, y: x + y)

    # Print the User tweet counts
    user_counts.pprint()

    # Start Execution of Streams
    ssc.start()
    ssc.awaitTermination()


if __name__ == "__main__":
    main()