import os
import time
import logging as log
import argparse

config = None

class Main:

	def __init__(self):
		"""
		Entry point of the simulation
		"""

		global config

		self.number_of_objects = 17 # placeholder until Jacob implements his image segmentation stuff
		self.use_image_models = config.args.imagemodels # whether or not to use the image models
		# using the image models takes a really long time (13 hours the last time I ran it) and they
		# reduce the accuracy from 69% to 64%

		if config.args.robot:
			robot.connect(config.args.address)

		self._init_logger()

		db.init_driver()
		db.connect(config.args.dbaddress, config.args.username, config.args.password, config.args.database, unix_socket=config.args.socket)

		# TODO: recognize which objects are new vs. old, categorize using classifiers,
		# ask for the new objects' names (probably extracted with Natalie's code),
		# and insert them into the database

		if config.args.setup:
			self.setup()

		if robot.robot():
			log.info("Robot is counting objects")
			self.number_of_objects = robot.robot().count_objects()
			robot.robot().say("I see %d objects" % self.number_of_objects, False)
			log.info("%d objects detected", self.number_of_objects)
			self.number_of_objects = 17

		# runtime does not include the time it took to run setup since it should only be run once
		start = time.time()
		self.simulate()
		end = time.time()

		log.info('Simulation complete! (Took %ds)', int(end - start))


	def simulate(self):
		"""
		Run the simulation
		"""

		log.info('Starting simulation')

		games_folder = os.getcwd() + '/Human_Games'

		wins = 0
		losses = 0
		num_questions = 0
		avg_win = 0
		avg_lose = 0
		questions_asked = {}
		question_answers = {}

		# TODO: Noelle - calibrate your gaze tracker here, unless it's better to do it at the beginning of every game/round

		for number in range(16, 31):
			# TODO: make the number of games configurable??
			game = Game(number)

			game_wins, game_losses, game_num_questions, game_win_avg, game_lose_avg, game_answers, game_questions = game.playGame(self.number_of_objects)

			# dictionaries with complete list of questions asked and the corresponding answers
			questions_asked[game.id] = game_questions
			question_answers[game.id] = game_answers

			# averages will be computed at the end of the program; for now these are just sums
			wins += game_wins
			losses += game_losses
			num_questions += game_num_questions
			avg_win += game_win_avg
			avg_lose += game_lose_avg

			if self.use_image_models:
				# image models are built after every single game
				models.build(game, 3, self.number_of_objects, questions_asked, question_answers)

			if config.args.notsimulated:
				quit = interface.ask("Would you like to stop playing completely? \nThere are %d games left. " % (30 - number))
				if quit == "yes":
					break

		log.info("Overall Wins: %d Overall Losses: %d", wins, losses)
		log.info("Overall Accuracy: %d%%", int((float(wins)/(wins + losses)) * 100))
		if wins != 0:
			log.info("Average number of questions for a win: %.2f", float(avg_win)/wins)
		if losses != 0:
			log.info("Average number of questions for a loss: %.2f", float(avg_lose)/losses)

		if config.args.robot:
			# TODO: remove this when we fix the robot class
			robot.broker.shutdown()

	def setup(self):
		"""
		Perform optional pre-simulation tasks, should only have to be run once
		as long as you setup with the image models the first time
		"""

		log.info('Performing setup')
		db.cursor.execute('DELETE FROM Pqd')
		db.connection.commit()
		db.cursor.execute('DELETE FROM answers')
		questions.copy_into_answers()
		questions.build_pqd(self.number_of_objects)
		if self.use_image_models:
			models.build(Game(0), 3, self.number_of_objects)
			models.build(Game(15), 3, self.number_of_objects)


	def _init_logger(self):
		"""
		Setup logger
		"""

		log.basicConfig(level='DEBUG', format='[ %(levelname)-5.5s]  %(message)s')
		rootLogger = log.getLogger()

		fileFormatter = log.Formatter('%(asctime)s [ %(levelname)-5.5s]  %(message)s')
		fileHandler = log.FileHandler('log.txt')
		fileHandler.setFormatter(fileFormatter)
		rootLogger.addHandler(fileHandler)

		log.info('\n'*8 + '='*31 + '| NEW SIMULATION |' + '='*31 + '\n')


def _config():
	"""
	Imports config.py or generates a default one if it doesn't exist
	Also parses command line arguments
	"""

	try:
		import config
	except ImportError:
		f = open('config.py', 'w')
		f.write("db = {\n\t'address': 'localhost',\n\t'username': 'root',\n\t'password': 'root',\n\t'database': 'iSpy_features',\n\t'socket': '/var/run/mysqld/mysqld.sock'\n}\n\nrobot = {\n\t'address': 'bobby.local'\n}")
		f.close()
		import config

	# you can set the defaults by changing the config file or specify a temporary change using command line flags
	parser = argparse.ArgumentParser()
	parser.add_argument("-i", "--imagemodels", action="store_true", help="use image models")
	parser.add_argument("-s", "--setup", action="store_true", help="run setup")
	parser.add_argument("-n", "--notsimulated", action="store_true", help="user provides responses")
	parser.add_argument("-u", "--username", help="database username", default=config.db["username"])
	parser.add_argument("-p", "--password", help="database password", default=config.db["password"])
	parser.add_argument("-d", "--database", help="choose which database to use", default=config.db["database"])
	parser.add_argument("-a", "--dbaddress", help="address of MySQL server", default=config.db["address"])
	parser.add_argument("-t", "--socket", help="path to MySQL socket", default=config.db["socket"])
	parser.add_argument("-r", "--robot", action="store_true", help="runs code using robot")
	parser.add_argument("--address", help="the robot's ip address", default=config.robot["address"])

	args = parser.parse_args()

	if args.robot:
		#if you're using the robot then by default you have to provide the answers
		args.notsimulated = True

	config.args = args

	return config

if __name__ == '__main__':
	config = _config()
	from game import Game
	import models
	import questions
	import database as db
	import robot
	import interface
	Main()
