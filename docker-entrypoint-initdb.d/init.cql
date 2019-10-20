create keyspace Inappropriate_Language_Detection with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
use Inappropriate_Language_Detection;
create table inappropriate_tweets (tweet text, username text, prediction int, date text, country text, primary key (tweet));

