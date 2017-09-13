#This program contains all the behavior functions
from naoqi import ALProxy
IP = "192.168.1.111"
PORT = 9559
NAME = "Breanna" #enter name of participant
DESCRIPTOR = "the blue book" #insert part of the question  

#This is a helper function for making the robot move
def motion(part, a, b, c, d):
	global IP
	global PORT
	motion = ALProxy("ALMotion", IP, PORT)
	motion.setStiffnesses(part, 1.0)
	id = motion.post.angleInterpolation(
		[part],
		[a, b],
		[c, d],
		False
		)
	motion.setStiffnesses(part, 1.0)
	motion.wait(id, 0)

#This function introduces the robot and player to each other
def intro():
	global IP
	global PORT
	global NAME
	aas = ALProxy("ALAnimatedSpeech", IP, PORT)
	tts = ALProxy("ALTextToSpeech",IP, PORT)
	postureProxy = ALProxy("ALRobotPosture", IP, 9559)
	aas.say("Hi,^run(animations/Stand/Gestures/Hey_1) My name is Bobby! ^run(animations/Stand/Gestures/You_1) What is your name?")
	postureProxy.goToPosture("Stand", 1.0)
	tts.say("Nice to meet you" + NAME)

#This function shakes hand with the human player
def shake():
	global IP
	global PORT
	move = ALProxy("ALMotion", IP, PORT)
	tts    = ALProxy("ALTextToSpeech", IP, PORT)
	motion("RShoulderPitch", -1.5, -1.5, 1, 2)
	move.setStiffnesses("RHand", 1.0)
	move.openHand("RHand")
	move.setStiffnesses("RHand", 1.0)
	tts    = ALProxy("ALTextToSpeech", IP, PORT)
	tts.say("Let's shake hands!")
	move.setStiffnesses("RHand", 1.0)
	move.closeHand("RHand")
	move.setStiffnesses("RHand", 1.0)
	tts    = ALProxy("ALTextToSpeech", IP, PORT)
	tts.say("Wow you have a strong grip!")
	motion("RShoulderPitch", 0.75, -0.75, 1, 2)
	motion("RShoulderPitch", 0.75, 0.75, 1, 2)
	move.setStiffnesses("RHand", 1.0)
	move.openHand("RHand")
	move.setStiffnesses("RHand", 1.0)
	motion("RShoulderPitch", 1.5, 1.5, 1, 2)
	move.setStiffnesses("RHand", 1.0)
	move.closeHand("RHand")
	move.setStiffnesses("RHand", 1.0)
	tts    = ALProxy("ALTextToSpeech", IP, PORT)
	tts.say("Nice to meet you!")

#This function explains the instructions of the game to the human player
def instructions():
	global IP
	global PORT
	#Creates proxy that allows access to postures
	postureProxy = ALProxy("ALRobotPosture", IP, PORT)
	postureProxy.goToPosture("Stand", 1.0)
	#Creates proxy for text to speech
	tts = ALProxy("ALTextToSpeech", IP, PORT)
	tts.say("Are you ready to learn how to play?")
	#Creates proxy that uses animated speech
	aas    = ALProxy("ALAnimatedSpeech", IP, PORT)
	aas.say("Ok,^start(animations/Stand/BodyTalk/BodyTalk_1) so basically what you are going to do is look at these 17 objects.")
	aas.say("Then you are going to pick one object,^start(animations/Stand/BodyTalk/BodyTalk_2) and not tell me which one it is.")
	aas.say("I am going to ask you questions about the object you are thinking of,^start(animations/Stand/BodyTalk/BodyTalk_3) and you can only answer by saying yes or no!")
	aas.say("Once I think I know what the object is,^start(animations/Stand/BodyTalk/BodyTalk_4) I will guess, and you will tell me if I am right or wrong!")
	aas.say("We will play 5 games this way,^start(animations/Stand/BodyTalk/BodyTalk_6) and then switch roles and play five more games!")
	tts.say("Are you ready to begin playing?")

#This function shrugs/expresses not knowing 
def shrug():
	tts = ALProxy("ALTextToSpeech", IP, 9559)
	postureProxy = ALProxy("ALRobotPosture", IP, 9559)
	postureProxy.goToPosture("Stand", 1.0)
	motion = ALProxy("ALMotion", IP, 9559)
	motion.setStiffnesses("RHand", 1.0)
	motion.openHand("RHand")
	motion.setStiffnesses("RHand", 1.0)
	motion.setStiffnesses("LHand", 1.0)
	motion.openHand("LHand")
	motion.setStiffnesses("LHand", 1.0)
	motion.setStiffnesses("LElbowYaw", 1.0)
	motion.post.angleInterpolation(
		["LElbowYaw"],
		[-2.7, -2.7],
		[1  , 2],
		False
		)
	motion.setStiffnesses("LElbowYaw", 1.0)
	motion.setStiffnesses("RElbowYaw", 1.0)
	motion.post.angleInterpolation(
		["RElbowYaw"],
		[2.7, 2.7],
		[1  , 2],
		False
		)
	motion.setStiffnesses("RElbowYaw", 1.0)
	motion.setStiffnesses("LWristYaw", 1.0)
	motion.post.angleInterpolation(
		["LWristYaw"],
		[-1.8, -1.8],
		[1  , 2],
		False
		)
	motion.setStiffnesses("LWristYaw", 1.0)
	motion.setStiffnesses("RWristYaw", 1.0)
	motion.post.angleInterpolation(
		["RWristYaw"],
		[1.8, 1.8],
		[1  , 2],
		False
		)
	motion.setStiffnesses("RWristYaw", 1.0)
	motion.setStiffnesses("LElbowRoll", 1.0)
	motion.post.angleInterpolation(
		["LElbowRoll"],
		[-1.5, -1.5],
		[1  , 2],
		False
		)
	motion.setStiffnesses("LElbowRoll", 1.0)
	motion.setStiffnesses("RElbowRoll", 1.0)
	motion.post.angleInterpolation(
		["RElbowRoll"],
		[1.5, 1.5],
		[1  , 2],
		False
		)
	motion.setStiffnesses("RElbowRoll", 1.0)
	motion.setStiffnesses("LShoulderRoll", 1.0)
	motion.post.angleInterpolation(
		["LShoulderRoll"],
		[.62, .62],
		[1  , 2],
		False
		)
	motion.setStiffnesses("LShoulderRoll", 1.0)
	motion.setStiffnesses("RShoulderRoll", 1.0)
	motion.post.angleInterpolation(
		["RShoulderRoll"],
		[-.62, -.62],
		[1  , 2],
		False
		)
	motion.setStiffnesses("RShoulderRoll", 1.0)
	tts.say("Ummm... this is a hard one!")
	motion.setStiffnesses("LShoulderPitch", 1.0)
	motion.post.angleInterpolation(
		["LShoulderPitch"],
		[-.62, 0],
		[1  , 2],
		False
		)
	motion.setStiffnesses("LShoulderPitch", 1.0)
	motion.setStiffnesses("RShoulderPitch", 1.0)
	id = motion.post.angleInterpolation(
		["RShoulderPitch"],
		[-.62, 0],
		[1  , 2],
		False
		)
	motion.wait(id, 0)
	motion.setStiffnesses("RShoulderPitch", 1.0)
	postureProxy.goToPosture("Stand", 1.0)

#This function has the robot go to the stand position
def stand():
	global IP
	global PORT
	postureProxy = ALProxy("ALRobotPosture", IP, 9559)
	postureProxy.goToPosture("Stand", 1.0)

#This function allows a custom question
def question():
	global IP
	global PORT
	global DESCRIPTOR
	tts = ALProxy("ALTextToSpeech",IP, PORT)
	tts.say("Is it" + DESCRIPTOR + "?" )

#This function celebrates a win
def win():
	global IP
	global PORT
	aas = ALProxy("ALAnimatedSpeech", IP, PORT)
	aas.say("Yay!^run(animations/Stand/Gestures/Enthusiastic_5)")

#This function is for when it loses
def lose():
	global IP
	global PORT
	aas = ALProxy("ALAnimatedSpeech", IP, PORT)
	aas.say("This sucks!^run(animations/Stand/Gestures/No_9)")

#This function thanks the player for participating
def thanks():
	global IP
	global PORT
	aas = ALProxy("ALAnimatedSpeech", IP, PORT)
	aas.say("Thank you so much for playing with me!^run(animations/Stand/Gestures/BowShort_1)")

stand()
shake()