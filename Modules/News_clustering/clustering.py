from .c_functions import generate_similarity_matrix, generate_threshold, similar_docs, entity_content
from Modules import connect_db
import json

ENTITY_COLLECTION_NAME = 'entity_data'


class NewsClusters:
    def __init__(self, input_data=None, account_name=None):
        self.extracted_data = input_data
        self.collection_name = account_name + '_' + ENTITY_COLLECTION_NAME
        self.entity_instance = connect_db.entity_dbinstance(collection_name=self.collection_name)

    def similarity_matrix(self):
        similarity_matrix = generate_similarity_matrix(listofarticles=self.extracted_data)
        threshold = generate_threshold(similarity_value_matrix=similarity_matrix)
        return similarity_matrix, threshold

    def generate_clusters_with_document_nos(self):
        """
        :return: a list of lists. Each nested list is an entity that contains the document nos
                that have been clustered together. --> [[23],[1,6,88],[45,33] ....]
        """
        clusters = []
        similarity_matrix, threshold = self.similarity_matrix()
        number_of_articles = len(similarity_matrix)
        input_article = 0
        clustered_article_no = []
        while input_article < number_of_articles:
            clustered_article_no = list(set(clustered_article_no))
            if input_article not in clustered_article_no:
                current_cluster = [input_article]
                similar_articles = similar_docs(doc_no=input_article, similarity_matrix=similarity_matrix,
                                                threshold=threshold, cluster=current_cluster)

                clustered_article_no.extend(similar_articles)
                clusters.append(current_cluster)
            input_article = input_article + 1
        return clusters

    def create_entities(self):
        """
        updates the mongo db directly in the "entity_data" db entity wise

        """
        entity_no = 1
        f = []
        cluster_with_documentnos = self.generate_clusters_with_document_nos()
        total_no_of_entities_today = len(cluster_with_documentnos)
        for item in range(total_no_of_entities_today):
            entity = entity_content(cluster_docnos=cluster_with_documentnos[item],
                                    db_collection=self.extracted_data, number=entity_no)
            self.entity_instance.insert_one(entity)
            entity_no += 1
            f.append(entity)

        output_file = open('test.json', 'w', encoding='utf-8')
        for dic in f:
            json.dump(dic, output_file)
            output_file.write(",\n")
        return 0


def getresponse(extracted_data=None, account_name=None):
    obj = NewsClusters(input_data=extracted_data, account_name=account_name )
    obj.create_entities()
