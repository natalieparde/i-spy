import config
from robot import robot

def ask(question):
	if robot():
		return robot().ask(question)
	else:
		while True:
			response = raw_input(question).lower()[0]
			if response == "y":
				return "yes"
			elif response == "n":
				return "no"

def say(text):
	if robot():
		robot().say(text)
	else:
		print text
