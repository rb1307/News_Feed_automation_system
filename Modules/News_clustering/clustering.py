import sys
sys.path.append("..")
import connect_db
from News_clustering import c_functions


class NewsClusters:
    def __init__(self):
        extract_db = connect_db.extracted_dbinstance()
        self.last_batch_articles = extract_db.find({})
        # self.number_of_articles = self.last_batch_articles.count()

    def similarity_matrix(self):
        similarity_matrix = c_functions.generate_similarity_matrix(docs=self.last_batch_articles)
        threshold = c_functions.generate_threshold(similarity_value_matrix=similarity_matrix)
        return similarity_matrix, threshold

    def generate_clusters(self):
        clusters = []
        similarity_matrix, threshold = self.similarity_matrix()
        # print(len(self.number_of_articles))
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


def getresponse():
    obj = NewsClusters()
    obj.generate_clusters()


getresponse()
