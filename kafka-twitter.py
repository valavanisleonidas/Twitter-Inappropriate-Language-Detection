import logging

from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
from kafka import SimpleProducer, SimpleClient
import twitter_config

consumer_key = twitter_config.consumer_key
consumer_secret = twitter_config.consumer_secret
access_token = twitter_config.access_token
access_token_secret = twitter_config.access_secret


class TwitterStreamListener(StreamListener):
    """
        This listener handles tweets that are received from the Twitter streaming API.
        This listener dumps the tweets into a Kafka topic
    """

    def __init__(self):
        # localhost:9092 = Default Zookeeper Producer Host and Port Adresses
        super().__init__()
        self.client = SimpleClient("localhost:9092")

        self.producer = SimpleProducer(self.client)

    def on_data(self, data):
        # send data to topic named twitter
        self.producer.send_messages("twitter", data.encode('utf-8'))
        # print(data)
        return True

    def on_error(self, status):
        print(status)


def main():
    logging.basicConfig(
        format='%(asctime)s.%(msecs)s:%(name)s:%(thread)d:%(levelname)s:%(process)d:%(message)s',
        level=logging.INFO
    )

    listener = TwitterStreamListener()

    # Twitter authentication and the connection to Twitter Streaming API
    auth = OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    stream = Stream(auth, listener)

    # stream.filter(track=['actian', 'BigData', 'Hadoop', 'Predictive', 'Quantum', 'bigdata', 'Analytics', 'IoT'])
    # stream.filter(track=['actian', 'hadoop', 'hadoopsummit'])
    # stream.filter(track="trump")

    # Sample delivers a stream of 1% (random selection) of all tweets
    stream.sample()


if __name__ == '__main__':
    main()
