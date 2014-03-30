# -----------------------------------------------------------------------------------
# 
# Authors: Christopher Lowetz, Justin Martinez, Hunter McElroy
# 
#
# Usage: 
# -- user defined topic
#       python tweetbeats.py <song_title> <instrument_number> <topic>
#
#		Ex. python tweetbeats.py harry_potter 0 "harry potter"
#
# -- random trending topic
#       python tweetbeats.py <song_title> <instrument_number>
# -----------------------------------------------------------------------------------

from midiutil.MidiFile import MIDIFile
from boto.mturk.connection import MTurkConnection
import sys
import random
import pygame
from boto.mturk.question import QuestionContent,Question,QuestionForm, Overview,AnswerSpecification,SelectionAnswer,FormattedContent,FreeTextAnswer
import io, json
import string
from time import sleep
import tweepy

MIN_TWEETS = 50 #Minimum # of results received before creating song

MyMIDI = MIDIFile(4) # Create the MIDIFile Object with 4 tracks

ACCESS_ID ='ENTER YOUR KEY HERE'
SECRET_KEY = 'ENTER YOUR KEY HERE'
#HOST = 'mechanicalturk.amazonaws.com'
HOST = 'mechanicalturk.sandbox.amazonaws.com'

'''IN SANDBOX MODE!!!'''

class TweetCollector():
    consumer_key = "ENTER YOUR KEY HERE"
    consumer_secret = "ENTER YOUR KEY HERE"
    access_key = "ENTER YOUR KEY HERE"
    access_secret = "ENTER YOUR KEY HERE"
    auth = None
    api = None

    def __init__(self):
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_key, self.access_secret)
        self.api = tweepy.API(self.auth)

    def CollectTweets(self, user_topic):
        # get trends (U.S. only)
        US_WOE_ID = 23424977 # U.S. code
        trends = self.api.trends_place(id = US_WOE_ID)

        # getting trending topics
        data = trends[0] 
        # grab the trends
        topics = data['trends']
        # grab the name from each trend
        topic_names = [topic['name'] for topic in topics]

        # either use user assigned topic or random trending topic
        if len(user_topic) > 0:
            query = user_topic
        else:
            query = random.choice(topic_names)

        # get tweets for topic
        try:
            tweets = self.api.search(q=query, count = 100, lang='en', result_type = 'mixed')
        except:
            tweets = None

        # create tweet text array to be passed to AMT
        tweet_array = []
        for tweet in tweets:
            tweet_array.append(tweet.text.encode(sys.stdout.encoding, errors='replace'))

        return (query, tweet_array)
 
class MTurk:
	ACCESS_ID =''
	SECRET_KEY = ''
	HOST = ''
	filename = 'log.txt'
	moods = [('happy',0),('sad',0),('confused',0)]
	moodList = [('Joy','1'),('Sadness','2'),('Anger','3'),('Fear','4'),
			 ('Trust','5'),('Distrust','6'),('Surprise','7'),('Anticipation','8')]
	moodIntensity = [('1 - Lowest','1'),('2','2'),('3','3'),('4','4'),
			 ('5','5'),('6','6'),('7','7'),('8 - Highest','8')]

	mtc = MTurkConnection
	def __init__(self, access_id, key, host):
		self.ACCESS_ID = access_id
		self.SECRET_KEY = key
		self.HOST = host
		self.data = []

	def changeCredentials(self,ACCESS_ID,SECRET_KEY,HOST):
		self.ACCESS_ID = ACCESS_ID
		self.SECRET_KEY = SECRET_KEY
		self.HOST = HOST

	def getHit(self,hitID):
		mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                      aws_secret_access_key=self.SECRET_KEY,
                      host=self.HOST)
		assignments = mtc.get_assignments(hitID)
		for assignment in assignments: #unique to number of assignments in HIT
			print "Answers of the worker %s" % assignment.WorkerId
			for question_form_answer in assignment.answers[0]:
				for value in question_form_answer.fields:
					print "%s" % (value)

	def approveHit(self, assignment_id):
		mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                      aws_secret_access_key=self.SECRET_KEY,
                      host=self.HOST)
		mtc.approve_assignment(assignment_id, feedback=None)

	def disableHit(self, hit_id):
		mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                      aws_secret_access_key=self.SECRET_KEY,
                      host=self.HOST)
		mtc.disable_hit(hit_id, response_groups=None)

	def getAllHits(self, hits):
		mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                      aws_secret_access_key=self.SECRET_KEY,
                      host=self.HOST)
		for hit in hits:
		    assignments = mtc.get_assignments(hit)
		    for assignment in assignments:
		        print "Answers of the worker %s" % assignment.WorkerId
		        for question_form_answer in assignment.answers[0]:
		            for key, value in question_form_answer.fields:
		                print "%s: %s" % (key,value)
		        mtc.approve_assignment(assignment.AssignmentId)
		        print "--------------------"
		    mtc.disable_hit(hit)

	def createHit(self,text):
		mtc = MTurkConnection(aws_access_key_id=self.ACCESS_ID,
                      aws_secret_access_key=self.SECRET_KEY,
                      host=self.HOST)
		overview = Overview()
		overview.append_field('Title','Rate this Tweet! (WARNING: This HIT may contain adult content. Worker discretion is advised.)')

		qc = QuestionContent()
		qc.append_field('Title','Please read the following: ')
		qc.append_field('Text', "\"" + text + "\"" +'\n')
		qc.append_field('Text','After reading the above tweet, please choose the mood which matches best with the content.')
		selectionAns = SelectionAnswer(min = 1, max = 1, style='radiobutton',
									   selections = self.moodList,
									   type="text",
									   other = False)
		q = Question(identifier='mood',
					 content = qc,
					 answer_spec = AnswerSpecification(selectionAns),
					 is_required=True)

		qc2 = QuestionContent()
		
		qc2.append_field('Text','Choose an intesity for the mood chosen.\n (1 - lowest | 10 - highest)')
		selectionAns2 = SelectionAnswer(min = 1, max = 1, style='radiobutton', #dropdown
									   selections = self.moodIntensity,
									   type="text",
									   other = False)
		q2 = Question(identifier='intensity',
					 content = qc2,
					 answer_spec = AnswerSpecification(selectionAns2),
					 is_required=True)

		question_form = QuestionForm()
		question_form.append(overview)
		question_form.append(q)
		question_form.append(q2)
		
		my_hit= mtc.create_hit(questions=question_form,
						max_assignments=1,
						title='Rate this Tweet! (WARNING: This HIT may contain adult content. Worker discretion is advised.)',
						description='Easy! Read a single tweet and rate choose a mood and intensity',
						keywords='rate, tweet',
						duration = 60*5, #60 seconds * 5
						reward = 0.01)
		return my_hit[0].HITTypeId 
		
	'''
	def writeLog(self,topic,ID):
		obj = {topic:ID} 
		print(json.dumps(obj))
		with io.open(self.filename,'a') as wfile:
			wfile.write(obj)
	'''
	#return 

hits2 = [(1,2),(3,4),(4,2),(3,5),(3,6),(4,0),(2,6),(2,4),(1,2),(3,4),(4,3),(0,2),(4,4),(1,4),(0,0),(5,4),(1,7),(2,6),(4,5),(1,2),(4,5),(4,2),(5,4),(5,5),(6,3),(1,2),(1,2),(4,5),(2,1),(3,6),(6,2),(5,1),(0,1),(2,3),(5,4),(1,0),(1,2),(3,5),(0,0),(0,3),(2,0),(1,1),(4,5),(2,0),(0,2),(5,4),(6,2),(2,0),(1,2),(2,3),(0,1),(2,1),(2,0),(1,4),(2,4),(5,2),(0,1),(2,2),(3,0),(2,0),(1,2),(1,2),(0,4),(5,3),(6,3),(3,0),(3,5),(1,0),(1,4),(1,2),(0,1),(2,1),(1,1),(0,1)]

def get_all_reviewable_hits(mtc):
    page_size = 50
    hits = mtc.get_reviewable_hits(page_size=page_size)
    print "Total results to fetch %s " % hits.TotalNumResults
    print "Request hits page %i" % 1
    total_pages = float(hits.TotalNumResults)/page_size
    int_total= int(total_pages)
    if(total_pages-int_total>0):
        total_pages = int_total+1
    else:
        total_pages = int_total
    pn = 1
    while pn < total_pages:
        pn = pn + 1
        print "Request hits page %i" % pn
        temp_hits = mtc.get_reviewable_hits(page_size=page_size,page_number=pn)
        hits.extend(temp_hits)
    return hits

def addChord(time, duration, volume, note1, note2, note3, note4):
	channel = 0
	
	#MyMIDI.addNote(track,channel,note1,time,duration,volume)
	# 	track : 
	# 	channel :
	#	note : midi pitch name
	# 	time : starting time in beats
	# 	duration : in beats
	# 	volume : 0-100

	if (note1 > -1):
		MyMIDI.addNote(0,channel,note1,time,duration,volume)
	if (note2 > -1):
		MyMIDI.addNote(1,channel,note2,time,duration,volume)
	if (note3 > -1):
		MyMIDI.addNote(2,channel,note3,time,duration,volume)
	if (note4 > -1):
		MyMIDI.addNote(3,channel,note4,time,duration,volume)
	#time += duration


def initializeTrack(instrument):
	# Tracks are numbered from zero. Times are measured in beats.

	#MyMIDI.addTrackName(track,time,name)
	MyMIDI.addTrackName(0,0,"Track 1")
	MyMIDI.addTrackName(1,0,"Track 2")
	MyMIDI.addTrackName(2,0,"Track 3")
	MyMIDI.addTrackName(3,0,"Track 4")

	#MyMIDI.addTempo(track,time,120)
	MyMIDI.addTempo(0,0,150)
	MyMIDI.addTempo(1,0,150)
	MyMIDI.addTempo(2,0,150)
	MyMIDI.addTempo(3,0,150)

	program = int(instrument) #93 (metallic pad), 11 (vibraphone), 101 (goblins) is good
	MyMIDI.addProgramChange(0, 0, 0, program)
	MyMIDI.addProgramChange(1, 0, 0, program)
	MyMIDI.addProgramChange(2, 0, 0, program)
	MyMIDI.addProgramChange(3, 0, 0, program)

def closeTrack(filename):
	# write track to disk.
	binfile = open(filename + ".mid", 'wb')
	MyMIDI.writeFile(binfile)
	binfile.close()

'''
Chord Mappings:
#addChord(time, duration, volume, note1, note2, note3, note4)
		# 	time : starting time in beats
		# 	duration : in beats
		# 	volume : 0-100
		# 	note : midi pitch name
addChord( 1, 4, 100, 60, 64, 67, -1) #C maj 	Joy
addChord( 5, 4, 100, 60, 63, 67, 70) #C min9	Sadness
addChord( 9, 4, 100, 60, 64, 66, 69) #C dim7	Anger
addChord(13, 4, 100, 60, 64, 66, -1) #C flat5	Fear
addChord(17, 4, 100, 60, 64, 67, 69) #C maj6	Trust
addChord(21, 4, 100, 60, 63, 67, 69) #C m6 		Distrust
addChord(25, 4, 100, 60, 63, 66, 70) #C m7b5	Surprise
addChord(29, 4, 100, 60, 64, 67, 71) #C maj7	Anticipation
addChord(time, whole, 000, 60, 60, 60, 60) #empty		empty

time = 1
for result in hits:

	duration = 0
	durationResult = results[1]
	if durationResult == 0:
		duration = .5
	elif durationResult == 1:
		duration = 1
	elif durationResult == 2:
		duration = 2
	elif durationResult == 3:
		duration = 3
	elif durationResult == 4:
		duration = 4

	time += duration

	chord = results[0]
	if chord == 0:
		addChord(time, duration, 100, 60, 64, 67, -1) #C maj 	Joy
	elif chord == 1:
		addChord(time, duration, 100, 60, 63, 67, 70) #C min9	Sadness
	elif chord == 2:
		addChord(time, duration, 100, 60, 64, 66, 69) #C dim7	Anger
	elif chord == 3:
		addChord(time, duration, 100, 60, 64, 66, -1) #C flat5	Fear
	elif chord == 4:
		addChord(time, duration, 100, 60, 64, 67, 69) #C maj6	Trust
	elif chord == 5:
		addChord(time, duration, 100, 60, 63, 67, 69) #C m6 	Distrust
	elif chord == 6:
		addChord(time, duration, 100, 60, 63, 66, 70) #C m7b5	Surprise
	elif chord == 7:
		addChord(time, duration, 100, 60, 64, 67, 71) #C maj7	Anticipation
'''

def main(argv):
	if (len(argv) < 2):
		print "Usage: tweetbeats.py <song_title> <instrument_number> <optional_topic>"
	else:
		user_topic = ""
		# check for command line argument
		if len(argv) > 2:
			user_topic = argv[2]

		'''
		 '  Gather Tweets
		'''
		print "Gathering Tweets..."
		tc = TweetCollector()
		results = tc.CollectTweets(user_topic)
		print "Topic: " + results[0]
		'''
		 '  Create Hits
		'''
		print "Creating HITs..."
		mtur = MTurk(ACCESS_ID, SECRET_KEY,HOST)
		for result in results[1]:
			res = filter(lambda x: x in string.printable, result)
			new_id = mtur.createHit(res)

		mtc = MTurkConnection(aws_access_key_id=ACCESS_ID, aws_secret_access_key=SECRET_KEY, host=HOST)

		hits = get_all_reviewable_hits(mtc)
		while (len(hits) < MIN_TWEETS):
			print "Not enough hits. Will try again in 10 seconds...."
			sleep(10)
			hits = get_all_reviewable_hits(mtc)

		hits3 = []
		for hit in hits:
			assignments = mtc.get_assignments(hit.HITId)
			for assignment in assignments:
				print "Answers of the worker %s" % assignment.WorkerId
				answers = []
				for question_form_answer in assignment.answers[0]:
					for value in question_form_answer.fields:
						answers.append(int(value))
				print "Responses : ", answers
				hits3.append(answers)
				mtc.approve_assignment(assignment.AssignmentId)
				print "--------------------"
			mtc.disable_hit(hit.HITId)

		#Remove unused HITS; make 5 passes to clean up as best we can
		print "Removing unused HITs... Pass #1 of 5"
		hits = mtc.get_all_hits()
		for hit in hits:
			mtc.disable_hit(hit.HITId)

		print "Removing unused HITs... Pass #2 of 5"
		sleep(20)
		hits = mtc.get_all_hits()
		for hit in hits:
			mtc.disable_hit(hit.HITId)

		print "Removing unused HITs... Pass #3 of 5"
		sleep(20)
		hits = mtc.get_all_hits()
		for hit in hits:
			mtc.disable_hit(hit.HITId)

		print "Removing unused HITs... Pass #4 of 5"
		sleep(20)
		hits = mtc.get_all_hits()
		for hit in hits:
			mtc.disable_hit(hit.HITId)

		print "Removing unused HITs... Pass #5 of 5"
		sleep(20)
		hits = mtc.get_all_hits()
		for hit in hits:
			mtc.disable_hit(hit.HITId)

		'''
		 '  Make Hits into Music
		'''
		initializeTrack(argv[1])
		time = 1
		for result in hits3:

			duration = 0
			durationResult = result[1]
			if durationResult == 1:
				duration = .375 		#dotted sixteenth
			elif durationResult == 2:
				duration = .5 	 		#eighth
			elif durationResult == 3:
				duration = .75 			#dotted eigth
			elif durationResult == 4:
				duration = 1 			#quarter
			elif durationResult == 5:
				duration = 1.5 			#dotted quarter
			elif durationResult == 6:
				duration = 2 			#half
			elif durationResult == 7:
				duration = 3 			#dotted half
			elif durationResult == 8:
				duration = 4 			#whole

			shift = random.choice([-11, -10, -9, -8, -7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11])

			chord = result[0]
			if chord == 1:
				addChord(time, duration, 100, 60 + shift, 64 + shift, 67 + shift, -1) #C maj 	Joy
			elif chord == 2:
				addChord(time, duration, 100, 60 + shift, 63 + shift, 67 + shift, 70 + shift) #C min9	Sadness
			elif chord == 3:
				addChord(time, duration, 100, 60 + shift, 64 + shift, 66 + shift, 69 + shift) #C dim7	Anger
			elif chord == 4:
				addChord(time, duration, 100, 60 + shift, 64 + shift, 66 + shift, -1) #C flat5	Fear
			elif chord == 5:
				addChord(time, duration, 100, 60 + shift, 64 + shift, 67 + shift, 69 + shift) #C maj6	Trust
			elif chord == 6:
				addChord(time, duration, 100, 60 + shift, 63 + shift, 67 + shift, 69 + shift) #C m6 	Distrust
			elif chord == 7:
				addChord(time, duration, 100, 60 + shift, 63 + shift, 66 + shift, 70 + shift) #C m7b5	Surprise
			elif chord == 8:
				addChord(time, duration, 100, 60 + shift, 64 + shift, 67 + shift, 71 + shift) #C maj7	Anticipation

			time += duration
		addChord(time, 4, 000, 60, 60, 60, 60) #silence to allow last note to fade out
		closeTrack(argv[0])

		music_file = argv[0] + ".mid" 
		# set up the mixer 
		freq = 44100 # audio CD quality 
		bitsize = -16 # unsigned 16 bit 
		channels = 2 # 1 is mono, 2 is stereo 
		buffer = 2048 # number of samples 
		pygame.mixer.init(freq, bitsize, channels, buffer) 
		# optional volume 0 to 1.0 
		pygame.mixer.music.set_volume(1.0) 
		
		pygame.mixer.music.load(music_file) 
		print "Music file %s loaded!" % music_file 
		clock = pygame.time.Clock() 
		pygame.mixer.music.play() 
		while pygame.mixer.music.get_busy(): 
			# check if playback has finished 
			clock.tick(30) 

if __name__ == "__main__":
    main(sys.argv[1:])