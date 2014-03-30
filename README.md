TweetBeats
============

Project for CSCE 438: Distributed Data-Intensive Systems @ Texas A&M University. Professor: James Caverlee

Twitter is a community of users sharing their opinions and thoughts about a
variety of topics. We have created a new way to "visualize" these opinions and
thoughts by creating an audible representation of tweets.

TweetBeats composes songs based on trending topics or a user specified topic
by using a crowdsourced evaluation of the mood of these tweets from Amazon Mechanical Turk. 

Dependencies
============

- Python 2.7
- Boto
You can use pip to install the latest released version of boto:
	pip install boto

How To Run
============

1) Ensure all dependencies are installed (see above).

2) In tweetbeats.py:
- Enter your Amazon Mechanical Turk API keys on lines 31 and 32. Note that HITs will be created in the AMT sandbox by default.
- Enter your Twitter API keys on lines 39-42 (in the TweetCollector function).

3) Run TweetBeats using one of the following commands:
 Usage: 
- user defined topic
	python tweetbeats.py <song_title> <instrument_number> <topic>
	Ex. python tweetbeats.py harry_potter 0 "harry potter"

- random trending topic
	python tweetbeats.py <song_title> <instrument_number>
	Ex. python tweetbeats.py trending_topic_song 0 

