# Twitter-Inappropriate-Language-Detection
Twitter Inappropriate Language Detection

Our project aims to perform inappropriate language detection in tweets. In order to do that, the tweets will be fetched from the Twitter Streaming API and temporarily stored in Apache Kafka. After storing the tweets in Kafka, there will be two consumers. Each consumer, using Spark streaming, will read the tweets from Kafka, preprocess and classify the tweets as inappropriate or not.

1. One consumer will create some analytics and save the results to Apache Cassandra NoSQL database. This analysis will group by results per re- gion/country/continent etc. which will be defined in later stages. Then, from the database, the data will be read, and Tableau will be used for visualization.
2. The other consumer will present analytics in real time using Tableau for visualization. This analysis will show the real-time statistics grouped by user (i.e. how many offensive tweets each user has).

The model predictions will be based on Machine Learning and Natural Lan- guage Processing (NLP) techniques.
