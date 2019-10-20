FROM openjdk:8

RUN update-ca-certificates -f \
  && apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y \
    software-properties-common \
    wget \
    git \
    libatlas3-base \
    libopenblas-base \
    libatlas-base-dev \
    build-essential \
  && apt-get clean

# Spark
RUN cd /usr/ \
  && wget "http://archive.apache.org/dist/spark/spark-2.4.3/spark-2.4.3-bin-hadoop2.7.tgz" \
  && tar xzf spark-2.4.3-bin-hadoop2.7.tgz \
  && rm spark-2.4.3-bin-hadoop2.7.tgz \
  && mv spark-2.4.3-bin-hadoop2.7 spark

ENV SPARK_HOME /usr/spark
ENV SPARK_MAJOR_VERSION 2
ENV PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.7-src.zip:$SPARK_HOME/python/:$PYTHONPATH

RUN mkdir -p /usr/spark/work/ \
  && chmod -R 777 /usr/spark/work/

ENV SPARK_MASTER_PORT 7077

# Miniconda
ENV CONDA_DIR /opt/miniconda
RUN wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh && \
    chmod a+x miniconda.sh && \
    ./miniconda.sh -b -p $CONDA_DIR && \
    rm ./miniconda.sh
ENV PATH="$CONDA_DIR/bin/":$PATH

RUN pip install --upgrade pip \
  && pip install pylint coverage pytest black --quiet

ENV PATH=$PATH:$SPARK_HOME/bin/
ENV PYSPARK_PYTHON python3


ADD kafka-consumer-realtime/kafka-consumer.py /
ADD model/predict_model.py /
ADD model model/

RUN pip install --upgrade pip && \
  pip install pyspark && \
  pip install numpy && \
  pip install nltk && \
  pip install pandas && \
  pip install pytest && \
  pip install twython && \
  pip install scikit-learn && \
  pip install tweepy

CMD PYSPARK_PYTHON=python3 $SPARK_HOME/bin/spark-submit --packages org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.3 kafka-consumer.py
# CMD ["PYSPARK_PYTHON=python3" , "$SPARK_HOME/bin/spark-submit" , "--packages" , "org.apache.spark:spark-streaming-kafka-0-8_2.11:2.4.3" , "kafka-consumer.py"]

        
