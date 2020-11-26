from pymongo import MongoClient
import json
# import spacy
# from spacy import displacy
from collections import Counter
# import en_core_web_sm
# nlp = en_core_web_sm.load()
import collections
import nltk
from nltk.tokenize import word_tokenize
from nltk.tag import pos_tag
from nltk.corpus import stopwords
import itertools
import operator
from numpy import dot
from numpy.linalg import norm
nltk.download('stopwords')


