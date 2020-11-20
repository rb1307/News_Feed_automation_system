import InputMethods
from pymongo import MongoClient
import CommonFunctions
import logging

username, password = InputMethods.getdb_credentials(path='/home/hp/NFA-System/Modules/',
                                                    file_name='mongodb_credentials.json')

client_cluster =MongoClient("mongodb+srv://"+username+":"+password+
                     "@cluster0.d8xlm.mongodb.net/<dbname>?retryWrites=true&w=majority")


def input_dbinstance():
    input_db = client_cluster['NFA_system']['input_db']
    return input_db


def aggregated_dbinstance():
    aggrg_db=client_cluster['NFA_system']['aggregated_data']
    return aggrg_db


def extracted_dbinstance():
    extr_db = client_cluster['NFA_system']['extracted_data']
    return extr_db


def move_last_data(extractor_db=None, aggregator_db=None):
    aggregator_db.remove({})
    #extr_db = client_cluster['NFA_system']['extracted_data']
    archive_db = client_cluster['NFA_system']['news_archive']
    latest_docs = extractor_db.find({})
    datetime_string = CommonFunctions.get_current_time_string()
    date = datetime_string.get("current_date")
    no_extracted_docs_latest = latest_docs.count()
    if no_extracted_docs_latest> 0:
        logging.info(str(no_extracted_docs_latest)+ " stories found in the extractor db. Moving them to news archive.")
        archive_db.insert_many(latest_docs)
        logging.warning("Cleaning the extractor_db")
        extractor_db.remove({})
    archive_db.update_many({}, {'$set': {'batch_id': date+'_001'}})
    return 0


