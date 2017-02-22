###############################################################################
#
# question_generator.py
#
# Automatically generates syntactically-correct surface realizations of yes/no
# questions about learned attributes.
#
###############################################################################

import os
import re
import json
import nltk
import random
import collections
from googleapiclient.discovery import build

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

   # Get the Google search result totals for:
   # - the exact surface realization
   # - the attribute word in the question
   # - the surface realization, allowing a "wildcard" in place of the attribute word
   def get_search_result_counts(self, question, word, template):
      api_key = "AIzaSyBIdqWQXYDpGLWgh3z2QEY4lnRv8CSjSzU"  # Enter your Google API key here.
      cse_id = "007446023248893782813:jvy6fqoh1km"  # Enter your custom search engine ID here.

      # Check the record of terms that have already been searched to determine
      # whether or not a new search needs to be created.  Not necessary, but useful
      # since we only have a limited number of free searches.
      if not os.path.exists("search_cache.json"):
         open("search_cache.json", "a").close()  # Create the cache file if it doesn't exist.

      # Read the data, and index it by search term, so the dictionary is: key:search term -> value:json object.
      cache_data = open("search_cache.json")
      cache_dict = {}
      for line in cache_data:
         columns = line.split("||")  # Columns are delimited by double pipes.
         json_line = json.loads(columns[1])
         cache_dict[columns[0]] = json_line  # key: term -> value: json line
      cache_data.close()

      # Now re-open the file for writing.
      cache_writer = open("search_cache.json", "a")

      # Checking for the exact surface realization....
      search_param = "\"" + question + "\""

      # Check to see if the search parameter is included in the cached results.
      if search_param in cache_dict:
         self.question_results = cache_dict[search_param]
      else:  # Run a new search.
         service = build("customsearch", "v1", developerKey=api_key)
         self.question_results = service.cse().list(q=search_param, exactTerms=question.strip('?!.').strip(), cx=cse_id).execute()

         # Add the results to the cache.
         cache_writer.write(search_param + "||" + json.dumps(self.question_results) + "\n")
      self.question_results_count = self.question_results["searchInformation"]["totalResults"]


      # Checking for the attribute word in the question....
      search_param = word

      # Check to see if the search parameter is included in the cached results.
      if search_param in cache_dict:
         self.word_results = cache_dict[search_param]
      else:  # Run a new search.
         service = build("customsearch", "v1", developerKey=api_key)
         self.word_results = service.cse().list(q=search_param, cx=cse_id).execute()

         # Add the results to the cache.
         cache_writer.write(search_param + "||" + json.dumps(self.word_results) + "\n")
      self.word_results_count = self.word_results["searchInformation"]["totalResults"]


      # Checking for the surface realization, allowing a "wildcard" (*) instead of the attribute word.
      search_param = "\"" + re.sub(r"<[^>]+>", "*", template) + "\""

      # Check to see if the search parameter is included in the cached results.
      if search_param in cache_dict:
         self.template_results = cache_dict[search_param]
      else:  # Run a new search.
         service = build("customsearch", "v1", developerKey=api_key)
         self.template_results = service.cse().list(q=search_param, exactTerms=search_param.strip("\"").strip('?!.').strip(), cx=cse_id).execute()

         # Add the results to the cache.
         cache_writer.write(search_param + "||" + json.dumps(self.template_results) + "\n")
      self.template_results_count = self.template_results["searchInformation"]["totalResults"]

      cache_writer.close()
      print "Question Results:", self.question_results_count
      print "Word Results:", self.word_results_count
      print "Template Results:", self.template_results_count

   def Main(self):
      self.build_templates()
      word = "orange"
      tag = self.get_pos_for_word(word)
      templates = self.get_templates_for_pos(tag)
      selected_template = self.select_template(templates)
      question = self.realize_question(word, selected_template)
      print question
      self.get_search_result_counts(question, word, selected_template)

if __name__ == '__main__':
   qg = QuestionGenerator()
   qg.Main()
