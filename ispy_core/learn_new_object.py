###############################################################################
#
# learn_new_object.py
#
# Contains functions associated with learning new objects during the I Spy
# game.
#
###############################################################################

import os
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

# Determines whether or not the robot already knows an object by this name,
# returning True if it does, and False if it does not.
def is_new(object_name):
   objects_known = []

   # Get the object names the robot already knows.
   if os.path.isfile("object_names_i_know.txt"):
      infile = open("object_names_i_know.txt")  # For now, store all the object names the robot has learned in a .txt file.   
      for line in infile:
         objects_known.append(line.strip())  # Object names are stored one per line.
      infile.close()

   # Check to see if this object name is one of the already-known names.
   if object_name in objects_known:  # If so, it's not really new.
      return False
   else:  # If not, then it really is new.
      outfile = open("object_names_i_know.txt", "a")  # Append this new name to the file that we read earlier; now we know it.
      outfile.write(object_name + "\n")
      outfile.close()
      return True

# Either tell the user it was just confused and really knew the object, or prompt
# for additional information about the object, depending on whether or not the
# object really is new.
def get_info(object_name):
   if is_new(object_name):
      print "Interesting!"

      # TODO: Get follow-up information here, browse for more details using the
      # Amazon product description dataset, etc.

      # TODO: Store this information somewhere and decide when to retrain the
      # relevant model(s) (maybe at the end of learning info about all the new
      # objects).
      return True
   else:
      print "Oh, that's what that is!  I already know about those; I just didn't recognize this one."

      # TODO: Ask the user if there's anything unusual about this particular <object_name>.
      # Extract concepts from the user's response and create/update those models using only
      # images of this object (not other images of <object_name> that the robot already has
      # stored in memory).
      return False
