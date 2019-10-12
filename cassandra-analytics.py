import pandas as pd
from cassandra.cluster import Cluster

cassandra_keyspace = "inappropriate_language_detection"
cassandra_table = "inappropriate_tweets"
kafka_topic = 'twitter'

cluster = Cluster()
session = cluster.connect(cassandra_keyspace)

# cluster = Cluster(['0.0.0.0'], port=9042)
# session = cluster.connect('cityinfo', wait_for_all_pools=True)


def main():
    query = 'SELECT * FROM inappropriate_tweets'
    session.execute('use Inappropriate_Language_Detection')

    # tweets = session.execute(query)
    # for tweet in tweets:
    #     print(tweet.tweet,tweet.username, tweet.date, tweet.prediction, tweet.country)

    df = pd.DataFrame(list(session.execute(query)))

    group = df.groupby('country')
    print(group.groups)



if __name__ == "__main__":
    main()
