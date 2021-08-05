"""
*******************************************
author : Romit Bhattacharyya
gmail : rbhattacharyya1307@gmail.com
*******************************************to extract the
Module is used to parse the rss feeds of different news websites to get the various component of news
e.g link, article body, tags, image etc.
"""

from CommonFunctions import parserssfeedresponse, extractrssresponse, required_datetime, check_for_testing_flag
import logging
import connect_db

logging.basicConfig(level=logging.INFO)

sources = ['Business Standard', 'Livemint', 'Times of India', 'The Hindu',
           'The New Indian Express', 'Dailythanthi', 'Dinakaran,Dinamani', 'Hindu thamil thisai']


class RssFeedExtractor:
    def __init__(self, **kwargs):
        self.values = {}
        self.values.update(kwargs)
        database = self.values.get("db_connect")
        self.input_db = connect_db.input_dbinstance(collection_name=database)
        self.aggregated_db = connect_db.aggregated_dbinstance(collection_name=database)
        self.cutoff_datetime = required_datetime(no_of_days=self.values.get("timeline_start_date"),
                                                 hour_of_day=self.values.get("timeline_start_hour"),
                                                 minute_of_hour=self.values.get("timeline_start_min"))

    def get_rss_feeds(self):
        feed_details = []
        testing_flag = check_for_testing_flag(is_test=self.values.get('is_test'))
        if testing_flag:
            feed = (self.values.get("rss_url"))
            document = self.input_db.find_one({"feed": feed})
            feed_details.append(document)
            return feed_details
        else:
            db_cursor = self.input_db.find({})
            for documents in db_cursor:
                feed_details.append(documents)
        return feed_details

    def extract_article_links(self):
        input_feeds = self.get_rss_feeds()
        article_links = []
        for feed_details in input_feeds:
            rss_response = parserssfeedresponse(feed=feed_details.get("feed"),
                                                feed_language=feed_details.get("newspaper_language"))
            feed_data = extractrssresponse(response=rss_response, cut_off_date=self.cutoff_datetime)
            feed_details.update(feed_data)
            article_links.append(feed_details)

        return article_links


def get_source_obj(**kwargs):
    obj = RssFeedExtractor(**kwargs)
    resp = obj.extract_article_links()
    return resp
