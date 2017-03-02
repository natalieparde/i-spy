###############################################################################
#
# learn_new_object.py
#
# Contains functions associated with learning new objects during the I Spy
# game.
#
###############################################################################

import nltk
import random
import string

# Get the name of the new object.  Note: This dialogue should be adapted a bit
# for non-command-line use (e.g., we can get rid of "Enter its name here:" when
# an actual robot is asking the question).
def get_name():
   dialogue_choice = random.randint(0,3)

   # Randomly choose one of several dialogue variations, to reduce redundancy.
   raw_name = ""
   if dialogue_choice == 0:
      print "I don't think I recognize this object!  What is it?  Enter its name here: ",
      raw_name = raw_input()
   elif dialogue_choice == 1:
      print "Wait, what is this?  Enter its name here: ",
      raw_name = raw_input()
   elif dialogue_choice == 2:
      print "Hmm, I'm not sure what this is.  Can you tell me?  Enter its name here: ",
      raw_name = raw_input()
   elif dialogue_choice == 3:
      print "This object is new to me!  What is it called?  Enter its name here: ",
      raw_name = raw_input()

   # Some simple processing on the name the user provided.
   stopwords = list(set(nltk.corpus.stopwords.words("english")))
   stopwords.append("'s")
   stopwords.append("'d")
   stopwords.append("'ll")
   stopwords.append("'t")
   stopwords.append("'ve")
   raw_name = raw_name.lower()  # Convert to lowercase.
   raw_name_tokens = nltk.tokenize.word_tokenize(raw_name)  # Tokenize
   filtered_tokens = [word for word in raw_name_tokens if word not in stopwords]  # Remove stopwords.
   filtered_tokens = [word for word in filtered_tokens if word not in string.punctuation]  # Remove punctuation.
   processed_name = " ".join(filtered_tokens)  # Join the tokens back together with a single space between each token.
   return processed_name
