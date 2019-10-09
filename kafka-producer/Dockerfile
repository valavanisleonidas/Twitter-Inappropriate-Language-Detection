FROM python:3

ADD kafka-twitter.py /
ADD twitter_config.py /

RUN pip install tweepy
RUN pip install kafka-python

CMD [ "python", "./kafka-twitter.py" ]