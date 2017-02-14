###############################################################################
#
# question_generator.py
#
# Automatically generates syntactically-correct surface realizations of yes/no
# questions about learned attributes.
#
###############################################################################

import re
import nltk
import random
import collections

class QuestionGenerator:

   # Build question templates using the questions collected from the online
   # version of "I Spy," and store them in a dictionary organized by content
   # POS tag (e.g., "is it <JJ> ?" may be stored in the list of templates
   # associated with tag "JJ").
   def build_templates(self):
      # Read in the questions collected from the online version of "I Spy."
      print "Reading questions from the online version of \"I Spy\"...."
      online_question_file = open("collected_questions.txt")
      online_qs = []
      for line in online_question_file:
         # Add each question to a list, stripping off leading and trailing 
         # whitespace and normalizing capitalization.
         online_qs.append(line.strip().lower())
      online_question_file.close()

      # Build templates from each question by replacing all content words
      # (nouns, verbs, adjectives, and adverbs) with their POS tags.
      print "Extracting templates from questions...."
      templates = collections.defaultdict(list)  # This will be a dictionary of lists: key:POS -> value: list of templates for this POS tag.
      content_tags = ["JJ", "JJR", "JJS", "NN", "NNS", "NNP", "NNPS", "RB", "RBR", "RBS", "VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]
      self.tagger = nltk.tag.perceptron.PerceptronTagger()  # Load the tagger outside of the loop so it doesn't have to be loaded thousands of times, and make it accessible throughout the class (not just this function).
      for q in online_qs:
         contains_content_tags = []
         tokens = nltk.tokenize.word_tokenize(q)  # Tokenize the question.

         if len(tokens) > 2:  # Require that templates be created from questions containing three or more tokens on the basis that those with one or two tokens are almost guaranteed to actually be non-questions (e.g., user mistakenly typed "yes" or an object ID in the question field).
            tagged_tokens = self.tagger.tag(tokens)  # Get the POS tags for each token.

            # Build the template(s) for this question, removing one content POS tag per template.
            for x in range(0,len(tagged_tokens)):
               if tagged_tokens[x][1] in content_tags:  # tagged_tokens[x] is a tuple containing (token, tag), so [1] refers to the tag.
                  template = ""
                  counter = 0
                  for token, tag in tagged_tokens:
                     if counter == x:
                        template += "<" + tag + "> "
                     else:
                        template += token + " "
                     counter += 1

                  # Add the template to the list of templates associated with the
                  # content word that was replaced.
                  if tagged_tokens[x][1] not in templates:
                     templates[tagged_tokens[x][1]] = []  # Create the list associated with this tag if it doesn't already exist.
                  templates[tagged_tokens[x][1]].append(template.strip())  # Strip leading and trailing whitespace. 

      # Get the frequency with which templates occur.
      print "Computing template frequencies...."
      self.template_freqs = {}  # This'll be a nested dictionary: key: POS -> value:dict(key:template -> value:frequency)
      for tag in templates:
         self.template_freqs[tag] = collections.Counter(templates[tag])

   # Get all of the templates associated with the specified POS tag, and their frequencies.
   def get_templates_for_pos(self, tag):
      return self.template_freqs[tag]

   # Get the POS tag for the specified word.
   def get_pos_for_word(self, word):
      tokens = nltk.tokenize.word_tokenize(word)  # If we just try to tag the word without tokenizing it, the tagger treats each letter of the word as a token.
      tagged_tokens = self.tagger.tag(tokens)
      if len(tagged_tokens) > 1:
         print tagged_tokens
         print "Error!  There should be only one token here."
      else:
         return tagged_tokens[0][1]

   # Select the template to use for the question.
   def select_template(self, templates):
      if len(templates) < 5:  # Select the template that occurred most frequently.
         template = templates.most_common(1)
         return template[0][0]  # List of size one, template is the first element of the first tuple.
      else:  # Select randomly from among the top five templates.
         top_templates = templates.most_common(5)
         random_num = random.randint(0,4)
         return top_templates[random_num][0]  # randomth tuple, template is the tuple's first element.

   # Construct a surface realization for the sentence by inserting the specified
   # word into the correct location of the template.
   def realize_question(self, word, template):
      question = re.sub(r"<[A-Z]+>", word, template)  # Use a regular expression to replace the tag specification (e.g., "<JJ>") with the word.
      return question

   def Main(self):
      self.build_templates()
      word = "orange"
      tag = self.get_pos_for_word(word)
      templates = self.get_templates_for_pos(tag)
      selected_template = self.select_template(templates)
      question = self.realize_question(word, selected_template)
      print question

if __name__ == '__main__':
   qg = QuestionGenerator()
   qg.Main()
