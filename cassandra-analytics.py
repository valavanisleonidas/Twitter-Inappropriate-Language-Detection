import pandas as pd
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster

cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'


auth_provider = PlainTextAuthProvider(username='cassandra', password='cassandra')
cluster = Cluster(['127.0.0.1'], port=9042, auth_provider=auth_provider)

session = cluster.connect(cassandra_keyspace)


def main():

    query = 'SELECT * FROM inappropriate_tweets'

    # tweets = session.execute(query)
    # for tweet in tweets:
    #     print(tweet.tweet,tweet.username, tweet.date, tweet.prediction, tweet.country)

    df = pd.DataFrame(list(session.execute(query)))

    group = df.groupby('country')
    print(group.groups)



if __name__ == "__main__":
    main()
