# Twitter-Inappropriate-Language-Detection
Twitter Inappropriate Language Detection

Our project aims to perform inappropriate language detection in tweets. In order to do that, the tweets will be fetched from the Twitter Streaming API and temporarily stored in Apache Kafka. After storing the tweets in Kafka, there will be two consumers. Each consumer, using Spark streaming, will read the tweets from Kafka, preprocess and classify the tweets as inappropriate or not.

1. One consumer will create some analytics and save the results to Apache Cassandra NoSQL database. This analysis will group by results per region/country/continent etc. which will be defined in later stages. Then, from the database, the data will be read, and Tableau will be used for visualization.
2. The other consumer will present analytics in real time using Tableau for visualization. This analysis will show the real-time statistics grouped by user (i.e. how many offensive tweets each user has).

The model predictions will be based on Machine Learning and Natural Language Processing (NLP) techniques.


Dependencies

-Docker

RUNNING PROGRAM 

1. open docker
2. open terminal
3. cd /path/to/root/folder
4. docker-compose up -d --build



To see an interface of the container, logs, the results etc. open a browser and type the url http://DOCKER_HOST:9000. 
A web ui (portainer) will be shown. If it is run locally then http://localhost:9000. 
Create account and login to see containers.