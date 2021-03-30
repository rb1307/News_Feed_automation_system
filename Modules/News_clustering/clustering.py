import sys
sys.path.append("..")
import connect_db
from News_clustering import c_functions
# from CommonFunctions import get_current_datetime_string


class NewsClusters:
    def __init__(self):
        extract_db_instance = connect_db.extracted_dbinstance()
        db_cursor = extract_db_instance.find({})
        self.last_batch_articles = c_functions.getdocsfromdbcursor(cursor=db_cursor)
        self.entity_instance = connect_db.entity_dbinstance()
        # self.number_of_articles = self.last_batch_articles.count()

    def similarity_matrix(self):
        similarity_matrix = c_functions.generate_similarity_matrix(listofarticles=self.last_batch_articles)
        threshold = c_functions.generate_threshold(similarity_value_matrix=similarity_matrix)
        return similarity_matrix, threshold

    def generate_clusters_with_documentnos(self):
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
                similar_articles = c_functions.similar_docs(doc_no=input_article, similarity_matrix=similarity_matrix,
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
        cluster_with_documentnos = self.generate_clusters_with_documentnos()
        total_no_of_entities_today = len(cluster_with_documentnos)
        for item in range(total_no_of_entities_today):
            entity = c_functions.entity_content(cluster_docnos=cluster_with_documentnos[item],
                                      db_collection=self.last_batch_articles, number=entity_no)
            self.entity_instance.insert_one(entity)
            entity_no += 1

        return 0


def getresponse():
    obj = NewsClusters()
    obj.create_entities()


getresponse()