import time
from optparse import OptionParser

from naoqi import ALProxy
from naoqi import ALBroker
from naoqi import ALModule

from helpers.segment import find_objects


class SegmentationModule(ALModule):
	"""
	A module to handle object detection
	"""

	def __init__(self, name):
		ALModule.__init__(self, name)


	def look_for_objects(self):
		"""
		This method causes the robot to stand up and look around.
		Returns an array of objects
		"""

		return find_objects()

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

	global Segmentation
	Segmentation = SegmentationModule("Segmentation")

	while True:
		time.sleep(1)

main()
