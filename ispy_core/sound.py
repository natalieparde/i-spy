import time
import numpy as np
import speech_recognition as sr
import os

from naoqi import ALModule, ALProxy, ALBroker

class Transcriber(ALModule):
	def __init__(self, strName, address, port):
		ALModule.__init__(self, strName)
		self.outfile = None
		self.outfiles = [None]*3
		self.count = 9999999
		self.check = False

		self.audio = ALProxy("ALAudioDevice", address, port)
		self.audio.setClientPreferences(self.getName(), 48000, [1,1,1,1], 0, 0)

	def start(self):
		print "Starting Transcriber"
		print self.getName()
		self.audio.subscribe(self.getName())

	def stop(self):
		print "Stopping Transcriber"
		self.ALAudioDevice.unsubscribe(self.getName())
		if self.outfile != None:
			self.outfile.close()

	def processRemote(self, input_channels, input_samples, timestamp, input_buffer):
		print "listening"
		sound_data_interlaced = np.fromstring(str(input_buffer), dtype=np.int16)
		sound_data = np.reshape(sound_data_interlaced, (input_channels, input_samples), 'F')
		peak_value = np.max(sound_data)

		if peak_value > 7500:
			print "Peak:", peak_value
			self.count = 20

		self.count -= 1

		if self.count == 0:
			print "STOP"*50
			self.check = True

		if self.outfile == None:
			filename = "output.raw"
			self.outfile = open(filename, "wb")

		sound_data[0].tofile(self.outfile)

if __name__ == "__main__":
	broker = ALBroker("broker", "0.0.0.0", 0, "bobby.local", 9559)
	transcriber = Transcriber("ALTranscriber", "bobby.local", 9559)
	transcriber.start()

	while True:
		if transcriber.check:
			break
	transcriber.stop()
	os.system("sox -r 48000 -e signed -b 16 -c 1 output.raw speech.wav")

	r = sr.Recognizer()
	with sr.WavFile("speech.wav") as source:
		speech = r.record(source)
	try:
		possibilities = r.recognize(speech,True)
		for possibility in possibilities:
			for word in self.object_vocab:
				for syn in self.object_vocab[word]:
					if possibility["text"] == syn:
						print possibility
						self.broker.shutdown()

	except LookupError:
		self.say("I couldn't understand what you said. Please go to the computer and type the name of your object.")
		self.broker.shutdown()
		obj = raw_input("What object were you thinking of?")
		print obj

	exit(0)
