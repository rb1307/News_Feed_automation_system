import re
import nltk
from nltk.tokenize import word_tokenize
from numpy import dot
from numpy.linalg import norm
from nltk.tag import pos_tag
from collections import Counter
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
nltk.download('stopwords')
nltk.download('punkt')


en_stopwords = set(stopwords.words('english'))


def cleanhtmltags(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_relevant_words(all_words=[]):
    all_words=[x.lower() for x in all_words]
    all_words = [i for i in all_words if i]
    for word in all_words:
        if word in en_stopwords:
            all_words.remove(word)
    all_words=[word for word in all_words if word.isalnum()]
    return all_words


def stem_words(word_list=[]):
    ps = PorterStemmer()
    stemmed_words = []
    for words in word_list:
        w = ps.stem(words)
        stemmed_words.append(w)

    return stemmed_words


def get_tf_values(document=None, field=None):
    article = document.get(field)
    words = []
    article = cleanhtmltags(article)
    sentences = nltk.sent_tokenize(article)
    for sentence in sentences:
        words.extend(word_tokenize(sentence))
    words = get_relevant_words(all_words=words)
    words = stem_words(word_list=words)
    total_no_of_words = len(words)
    word_freq = Counter(words)
    tf_document = {}
    for key, value in word_freq.items():
        tf_value = float(value / total_no_of_words)
        tf_value = round(tf_value, 5)
        tf_document[key] = tf_value

    return tf_document


def get_idf_values(idf_input={}):
    idf = {}
    for key, value in idf_input.items():
        val = round(float(169/value), 5)
        idf[key] = val
    return idf


def generate_tf_idf_structure(docs=None, field=None):
    resp = []
    corpus_words = []
    for story in docs:
        doc_details = {}
        tf_value_document = get_tf_values(document=story, field=field)
        # story['tf'] = tf_value_document
        doc_details['story_title'] = story.get("title")
        doc_details['keywords'] = story.get("provided_keywords")
        doc_details['tf'] = tf_value_document
        resp.append(doc_details)
        doc_words = list(doc_details.get('tf').keys())
        corpus_words.extend(doc_words)

    words_in_doc = Counter(corpus_words)
    number_of_corpus_words = list(words_in_doc.keys())
    idf_matrix = get_idf_values(idf_input=words_in_doc)

    return idf_matrix, resp, number_of_corpus_words


def generate_tf_idf_matrix(docs=None, similarity_id=None):
    idf_matrix, document_details, total_corpus_words = generate_tf_idf_structure(docs=docs, field=similarity_id)
    # print (document_details[0])
    for doc in document_details:
        tf_idf_values = {}
        tf_values = doc.get("tf")
        for word, tf in tf_values.items():
            tf_idf = round(tf * idf_matrix.get(word), 4)
            tf_idf_values[word] = tf_idf
        doc['tf_idf'] = tf_idf_values
    print("The total number of words in the corpus is " + str(len(total_corpus_words)))

    tf_idf = []
    for docs in document_details:
        doc_tf_idf = [0] * len(total_corpus_words)
        words = list(docs.get("tf").keys())
        for word in words:
            position = total_corpus_words.index(word)
            doc_tf_idf[position] = docs.get("tf_idf").get(word)
        tf_idf.append(doc_tf_idf)
    # print ("The number of tf_idf lists identified are : " + len(tf_idf))

    return tf_idf, document_details


def cosine_similarity(doc1=[], doc2=[]):
    cos_sim = round(dot(doc1, doc2) / (norm(doc1) * norm(doc2)), 6)

    return cos_sim


def generate_similarity_matrix(db=None, similarity_id=None):
    tf_idf_matrix, stories = generate_tf_idf_matrix(docs=db, similarity_id=similarity_id )
    t_docs=(len(tf_idf_matrix))
    all_similarity_matrix=[]
    for query in range(t_docs):
        similarity_matrix=[0]*t_docs
        # print ("Query Document No :" + str(query) +" " + retrieved_docs[query].get("title"))
        for others in range(t_docs):
            query_document = tf_idf_matrix[query]
            other_doc = tf_idf_matrix[others]
            cosine_similarity_value = cosine_similarity(doc1=query_document, doc2=other_doc)
            # print ("Other Document ::"+ retrieved_docs[others].get("title")+":: with similarity : \n" +
            # str(cosine_similarity_value))
            similarity_matrix[others]=cosine_similarity_value
        # similarity_matrix = normalize_values(values = similarity_matrix)
        all_similarity_matrix.append(similarity_matrix)
    return all_similarity_matrix