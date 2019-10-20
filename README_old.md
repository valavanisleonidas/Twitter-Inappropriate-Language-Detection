# Twitter-Inappropriate-Language-Detection
Twitter Inappropriate Language Detection

Our project aims to perform inappropriate language detection in tweets. In order to do that, the tweets will be fetched from the Twitter Streaming API and temporarily stored in Apache Kafka. After storing the tweets in Kafka, there will be two consumers. Each consumer, using Spark streaming, will read the tweets from Kafka, preprocess and classify the tweets as inappropriate or not.

1. One consumer will create some analytics and save the results to Apache Cassandra NoSQL database. This analysis will group by results per region/country/continent etc. which will be defined in later stages. Then, from the database, the data will be read, and Tableau will be used for visualization.
2. The other consumer will present analytics in real time using Tableau for visualization. This analysis will show the real-time statistics grouped by user (i.e. how many offensive tweets each user has).

The model predictions will be based on Machine Learning and Natural Language Processing (NLP) techniques.




RUNNING PROGRAM 

install spark, kafka, cassandra

1. Start Apache Kafka (zookeeper , kafka) and Cassandra 
    sh start-zookeeper.sh
    sh start-kafka.sh
    sh start-cassandra.sh

2. Start Producer
    python3 kafka-twitter.py
    
    -check topic count of messages
        - $KAFKA_HOME/bin/kafka-run-class.sh kafka.tools.GetOffsetShell --broker-list localhost:9092,localhost:9093,localhost:9094 --topic twitter --time -1

    
3. Start Consumer1 (real-time analytics) 
    (Important NOTE: --package spark-streaming-kafka-x-x_x.xx:x.x.x changes according to your version in $SPARK_HOME/jars/spark-core_x.xx-y.y.y.jar)

    PYSPARK_PYTHON=python3 $SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.3 kafka-consumer.py


4. Start Consumer2 (save to cassandra)
    - install pyspark_cassandra (hard to do..)
        - git clone https://github.com/anguenot/pyspark-cassandra.git
        - cd pyspark_cassandra
        - sbt compile
        
    -  PYSPARK_PYTHON=python3 $SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.3,anguenot/pyspark-cassandra:2.4.0 --conf spark.cassandra.connection.host=127.0.0.1 kafka-consumer-cassandra.py 


CASSANDRA CONFIG :
create keyspace and table in Cassandra 

- $CASSANDRA_HOME/bin/cqlsh
- create keyspace Inappropriate_Language_Detection with replication = {'class': 'SimpleStrategy', 'replication_factor': 1};
- describe keyspaces;   
- use Inappropriate_Language_Detection;
- create table inappropriate_tweets (tweet text, username text, prediction int, date text, country text, primary key (tweet));





