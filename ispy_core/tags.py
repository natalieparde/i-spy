
import database as db

_tags = []
_questions = []

def get(question_id):
	"""
	Get a specific tag
	"""
	return get_all()[question_id-1]


def get_all():
	"""
	Get list of all tags
	Returns list in the form of [tag]
	"""

	global _tags
	if not _tags:
		db.cursor.execute('SELECT tag FROM Tags')
		result = db.cursor.fetchall()
		for tag in result:
			_tags.append(tag[0])
	return _tags

def get_questions():
	"""
	Gets list of all questions
	"""

	global _questions
	if not _questions:
		db.cursor.execute('SELECT question FROM questions')
		qs = db.cursor.fetchall()
		for question in qs:
			_questions.append(question[0])
	return _questions
