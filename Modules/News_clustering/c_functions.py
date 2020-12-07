import re
import nltk
from nltk.tokenize import word_tokenize
from numpy import dot
from numpy.linalg import norm
import statistics
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from CustomErrors import CosValueError
import math
# nltk.download('stopwords')
# nltk.download('punkt')


en_stopwords = set(stopwords.words('english'))


def generate_similarity_matrix(docs=None):
    tf_idf_matrix, stories = generate_tfidf_matrix(docs=docs)
    t_docs=(len(tf_idf_matrix))
    all_similarity_matrix=[]
    for query in range(t_docs):
        similarity_matrix=[0]*t_docs
        for others in range(t_docs):
            query_document = tf_idf_matrix[query]
            other_doc = tf_idf_matrix[others]
            cosine_similarity_value = cosine_similarity(doc1=query_document, doc2=other_doc)
            similarity_matrix[others]=cosine_similarity_value
        # similarity_matrix = normalize_values(values = similarity_matrix)
        all_similarity_matrix.append(similarity_matrix)
    return all_similarity_matrix


# creates a 2D matrix of tf_idf values for each doc
def generate_tfidf_matrix(docs=None):
    tf_values, corpus_words = generate_tf_eachdoc(docs=docs)
    unique_corpus_words, idf_matrix = generate_idf_values(docs=docs, word_list=corpus_words)
    document_values = tfidf_docvalues(tf_values=tf_values, idf_matrix=idf_matrix)
    tf_idf_matrix = []
    for doc_id, tf_idf in document_values.items():
        doc_tfidf = [0] * len(unique_corpus_words)
        words = list(tf_idf.keys())
        for word in words:
            word_position = unique_corpus_words.index(word)
            doc_tfidf[word_position] = tf_idf.get(word)
        tf_idf_matrix.append(doc_tfidf)

    return tf_idf_matrix, document_values


# return tf_idf values for corpus word
def tfidf_docvalues(tf_values=None, idf_matrix=None):
    document_values = {}
    for doc_id, tf_list in tf_values.items():
        tf_idf_values = {}
        tf_values = tf_list
        for word, tf in tf_values.items():
            tf_idf = round(tf * idf_matrix.get(word), 4)
            tf_idf_values[word] = tf_idf
        document_values[doc_id] = tf_idf_values
    return document_values


# returns tf_values for all words in each doc
def generate_tf_eachdoc(docs=None):
    doc_details = {}
    corpus_words = []
    for doc in docs:
        tf_value_document = get_tf_values(document=doc)
        doc_details[doc.get("article_id")] = tf_value_document
        # resp.append(doc_details)
        doc_words = list(tf_value_document.keys())
        corpus_words.extend(doc_words)
    return doc_details, corpus_words


# returns the idf value for each word in the corpus
def generate_idf_values(word_list=None, docs=None):
    wordswiththeirfrequencies = Counter(word_list)
    unique_corpus_words = list(wordswiththeirfrequencies.keys())
    idf = {}
    for key, value in wordswiththeirfrequencies.items():
        val = round(float(docs.count() / value), 5)
        idf[key] = val
    return unique_corpus_words, idf


# calculates the tf for each word in doc
def get_tf_values(document=None):
    article = cleanhtmltags(document.get("article_body"))
    words = word_tokenization(article=article)
    total_no_of_words = len(words)
    word_freq = Counter(words)
    tf_document = {}
    for key, value in word_freq.items():
        tf_value = round(float(value / total_no_of_words), 4)
        tf_document[key] = tf_value
    return tf_document


# cleaning the html tags
def cleanhtmltags(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


#  tokenize all words in a body
def word_tokenization(article=None):
    sentences = nltk.sent_tokenize(article)
    words = []
    for sentence in sentences:
        words.extend(word_tokenize(sentence))
    words = get_relevant_words(all_words=words)
    words = stem_words(word_list=words)

    return words


# stopwords, punctuation and null value removal
def get_relevant_words(all_words=[]):
    all_words=[x.lower() for x in all_words]
    all_words = [i for i in all_words if i]
    for word in all_words:
        if word in en_stopwords:
            all_words.remove(word)
    all_words=[word for word in all_words if word.isalnum()]
    return all_words


# removing morphological variants of a base word
def stem_words(word_list=[]):
    ps = PorterStemmer()
    stemmed_words = []
    for words in word_list:
        w = ps.stem(words)
        stemmed_words.append(w)

    return stemmed_words


def cosine_similarity(doc1=[], doc2=[]):
    try:
        cos_sim = round(dot(doc1, doc2) / (norm(doc1) * norm(doc2)), 6)
        return cos_sim
    except Exception:
        raise CosValueError()


# calculate the threshold for document similarity
def generate_threshold(similarity_value_matrix=[]):
    all_values = [item for sublist in similarity_value_matrix for item in sublist]
    all_values = replacenanvalues(data=all_values, replaced_value=0)
    average_similarity_score = float(sum(all_values)/len(all_values))
    standard_deviation = statistics.pstdev(all_values)
    threshold = average_similarity_score + (1.25*standard_deviation)
    return threshold


def replacenanvalues(data=[], replaced_value=None):
    data = [replaced_value if math.isnan(x) else x for x in data]
    return data


# recursive function to find all the similar documents for a doc
def similar_docs(doc_no=None, similarity_matrix=None, threshold=0.0, cluster=None):
    try:
        similarity_column = similarity_matrix[doc_no]
        new_cluster = []
        for values in similarity_column:
            if values > threshold:
                similar_doc_no = similarity_column.index(values)
                if similar_doc_no not in cluster:
                    new_cluster.append(similar_doc_no)
        cluster.extend(new_cluster)
        if len(new_cluster) == 0:
            return cluster
        elif len(new_cluster) > 0:
            for docs in new_cluster:
                similar_docs(doc_no=docs, similarity_matrix=similarity_matrix, threshold=threshold, cluster=cluster)
        return cluster
    except Exception as e:
        print(e)


