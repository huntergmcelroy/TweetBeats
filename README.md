TweetBeats
============

TweetBeats is a project for CSCE 438: Distributed Data-Intensive Systems @ Texas A&M University. Professor: James Caverlee

Twitter is a community of users sharing their opinions and thoughts about a
variety of topics. We have created a new way to "visualize" these opinions and
thoughts by creating an audible representation of tweets.

TweetBeats composes songs based on trending topics or a user specified topic
by using a crowdsourced evaluation of the mood of these tweets from Amazon Mechanical Turk. 

Dependencies
============

The following dependencies are required to use TweetBeats. A script `install_dependencies.sh`has been included to help streamline the process.

- Python 2.7
- Boto (http://boto.readthedocs.org/en/latest/)
> You can use pip to install the latest released version of boto:
	- `pip install boto`

- Tweepy (https://pythonhosted.org/tweepy/html/)
> You can use pip to install the latest released version of Tweepy:
	- `pip install tweepy`

- MIDIUtil (https://code.google.com/p/midiutil/)
> Must be installed by downloading from the above website or from the MIDIUtil directory included in this repository:
	- `cd MIDIUtil-0.89`
	- `python setup.py install`

- Pygame (http://pygame.org/download.shtml)
> Pygame can be downloaded from the above website or you can use pip to install the latest released version of Pygame:
	- `pip install pygame`
	
How To Run TweetBeats
============

1) Ensure all dependencies are installed (see above).

2) In tweetbeats.py:
> - Enter your Amazon Mechanical Turk API keys on lines 33 and 34. Note that HITs will be created in the AMT sandbox by default. If you decide to run out of sandbox, switch HOST from 'mechanicalturk.sandbox.amazonaws.com' to 'mechanicalturk.amazonaws.com'. Note: Your account will be charged roughly $.50 - $1.00 per run of TweetBeats.
> - Enter your Twitter API keys on lines 41-44 (in the TweetCollector function).

3) Run TweetBeats using one of the following commands:

- user defined topic
>	- `python tweetbeats.py song_title instrument_number topic`
>	- Ex: `python tweetbeats.py harry_potter 0 "harry potter"`

- random trending topic
>	- `python tweetbeats.py song_title instrument_number`
>	- Ex: `python tweetbeats.py trending_topic_song 0`

4) Wait for the AMT HITs generate and complete. Once the minimum number of HITs have completed, the generated song will play and the .mid file will be saved in the working directory. All unused HITs will be deleted.
