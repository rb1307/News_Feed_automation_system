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
        self.input_db=connect_db.input_dbinstance()
        self.aggregated_db=connect_db.aggregated_dbinstance()
        self.values.update(kwargs)
        # if self.values.get("db_connect"):
        #    self.aggregated_db.remove({})
        self.cutoff_datetime = required_datetime(no_of_days=self.values.get("timeline_start_date"),
                                             hour_of_day=self.values.get("timeline_start_hour"),
                                             minute_of_hour=self.values.get("timeline_start_min"))

    def getrssfeeds(self):
        feed_details = []
        # CONDITION : test run with a single rss_url and source
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

    def extractarticlelinks(self):
        inputfeeds = self.getrssfeeds()
        article_links =[]
        for feed_details in inputfeeds:
            rss_response = parserssfeedresponse(feed=feed_details.get("feed"),
                                            feed_language=feed_details.get("newspaper_language"))
            feed_response = extractrssresponse(response=rss_response, cut_off_date=self.cutoff_datetime)
            """logging.info("RSS Feed : " + str(feed_details.get("feed")) + ". Feed details extracted :\nMetadata : " +
                         str(feed_response.get("metadata")) +
                         "\nNumber of article links found within the extracted timeline :"
                         + str(len(feed_response.get("article_links"))) + "\n\n")"""
            feed_details.update(feed_response)
            article_links.append(feed_details)
            if self.values.get("db_connect"):
                self.aggregated_db.insert_one(feed_details)

        return article_links


def getsourceobj(**kwargs):
    obj = RssFeedExtractor(**kwargs)
    resp = obj.extractarticlelinks()
    return resp
