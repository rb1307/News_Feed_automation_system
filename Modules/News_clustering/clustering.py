import connect_db
from pymongo import MongoClient
import json
# import spacy
# from spacy import displacy
# import en_core_web_sm
# nlp = en_core_web_sm.load()


import itertools
import operator


class NewsClusters:
    def __init__(self):
        self.extract_db = connect_db.extracted_dbinstance()


    def generate_clusters(self):
        similarity_matrix =
