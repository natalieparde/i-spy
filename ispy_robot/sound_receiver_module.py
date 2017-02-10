import time
from optparse import OptionParser

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

import numpy as np

class SoundReceiverModule(ALModule):
	"""
	A module to record speech while a person is talking
	"""

	def __init__(self, name):
		ALModule.__init__(self, name)
		self.audio = ALProxy("ALAudioDevice")
		self.data = [[]] * 4
		self.count = 999999

	def start_processing(self):
		"""
		Subscribe to the audio stream and begin processing
		"""

		channel_flag = 3 # ALL_Channels: 0,  AL::LEFTCHANNEL: 1, AL::RIGHTCHANNEL: 2 AL::FRONTCHANNEL: 3  or AL::REARCHANNEL: 4.
		deinterleave = 0
		sample_rate = 16000
		self.data = [[]] * 4
		self.audio.setClientPreferences(self.getName(),  sample_rate, channel_flag, deinterleave )
		self.audio.subscribe(self.getName())


	def stop_processing(self):
		"""
		Unsubscribe from the audio stream and end processing
		Returns raw audio data
		"""

		self.audio.unsubscribe(self.getName())

		return self.data[0]


	def processRemote(self, num_channels, num_samples, timestamp, buffer):
		"""
		This is THE method that receives all the sound buffers from the "ALAudioDevice" module
		"""

		data = np.reshape(np.fromstring(str(buffer), dtype=np.int16), (num_channels, num_samples), 'F')
		for i in range(num_channels):
			self.data[i].append(data[i].tolist())

		peak_value = np.max(self.data)

		if peak_value > 7500:
			self.count = 30

		self.count -= 1

		if self.count == 0:
			self.check = True



def main():
	"""
	Boilerplate method to register the module
	"""

	parser = OptionParser()
	parser.add_option("--pip", dest="pip")
	parser.add_option("--pport", dest="pport", type="int")
	parser.set_defaults(pip="localhost", pport=9559)

	(opts, args_) = parser.parse_args()
	pip = opts.pip
	pport = opts.pport

	broker = ALBroker("broker", "0.0.0.0", 0, pip, pport)

	global SoundReceiver
	SoundReceiver = SoundReceiverModule("SoundReceiver")

	while True:
		time.sleep(1)

main()
