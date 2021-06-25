from  Modules import InputMethods
from pymongo import MongoClient
from Modules import CommonFunctions
import logging

DATABASE_NAME = 'Samagra-Patrika'

username, password = InputMethods.get_db_credentials(path='/home/rb1307/Samagra Patrika',
                                                     file_name='mongodb_credentials.json')
client_cluster = MongoClient("mongodb+srv://" + username + ":" + password +
                             "@cluster0.hjuda.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")


def input_dbinstance(collection_name=None):
    input_db = client_cluster[DATABASE_NAME][collection_name]
    return input_db


def aggregated_dbinstance(collection_name=None):
    aggregate_db = client_cluster[DATABASE_NAME][collection_name]
    return aggregate_db


def extracted_dbinstance(collection_name=None):
    extr_db = client_cluster[DATABASE_NAME][collection_name]
    return extr_db


def archive_dbinstance(collection_name=None):
    archive_db = client_cluster[DATABASE_NAME][collection_name]
    return archive_db


def entity_dbinstance(collection_name=None):
    entity_db = client_cluster[DATABASE_NAME][collection_name]
    return entity_db


def move_last_data(extractor_db=None, aggregator_db=None):
    """
    :param extractor_db:
    :param aggregator_db:
    :return:
    """
    batch_id = '001' # need to correct this
    archive_db = archive_dbinstance()
    logging.info("Connecting to Mongodb cluster.\n\tDatabase : NFA_system \n\tCollections : aggregated_db\n"
                 "Operation : Removing last aggregated news list")
    aggregator_db.remove({})
    latest_docs = extractor_db.find({})
    datetime_string = CommonFunctions.get_current_datetime_string()
    date = datetime_string.get("current_date")
    no_extracted_docs_latest = latest_docs.count()
    if no_extracted_docs_latest > 0:
        logging.info(str(no_extracted_docs_latest) + " stories found in the extractor db. Moving them to news archive.")
        archive_db.insert_many(latest_docs)
        logging.warning("Cleaning the extractor_db")
        extractor_db.remove({})
    # previous data being moved into archive_db
    archive_db.update_many({}, {'$set': {'batch_id': date + '_' + batch_id}})
    return 0
