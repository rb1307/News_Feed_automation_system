"""
@Romit Bhattacharyya
__main.py__. for aggregating and extracting of all the new articles from different news sources.

"""


import configargparse
import RssFeedExtractor
import CustomErrors
import connect_db
import logging


class DailyUpdates:
    def __init__(self):
        parser = configargparse.ArgParser()
        parser.add_argument('-c', '--config', required=False, is_config_file=True, help='config file path')
        parser.add_argument('--storage_path', required=False, type=str,
                            help='storage path for all TN daily updates file')
        parser.add_argument('--input_file', required=False, type=str,
                            help='Input file containing sources, ids, feed_ids etc. ')
        parser.add_argument('--db_connect', required=False, default=False, type=bool, help='Update to database')
        parser.add_argument('--run_aggr', required=False, type=bool,
                            help='Condition to run the rss fed aggregator {default: True}')
        parser.add_argument('--start_date', required=False, type=int,
                            help='Last number of days\' news should be craped {default : 1}')
        parser.add_argument('--start_hour', required=False, type=int,
                            help='hoto starur of the day to scraping {default : 0}')
        parser.add_argument('--start_min', required=False, type=int,
                            help='minute of the hour to start scraping {default :0 }')
        parser.add_argument('--aggr_limit', required=False, type=bool, help='to limit the aggregation of rss feeds')
        parser.add_argument('--aggr_limit_value', required=False, type=int, help='no of articles aggregation to limit')
        parser.add_argument('--rss_url', required=False, type=str, help='rss feed for aggregation')
        parser.add_argument('--article_url', required=False, type=str, help='article url for scraping')
        parser.add_argument('--run_extr', required=False, type=bool,
                            help='Condition to run the article extractor {default = True')
        parser.add_argument('--extr_limit', required=False, type=bool, help='to limit the extraction of article bodies')
        parser.add_argument('--extr_limit_value', required=False, type=int, help='no of article extraction to limit')
        parser.add_argument('--source_id', required=False, type=str, help='list of sources to run DailyUpdates')
        parser.add_argument('--test', required=False, type=bool, default=False,  help='unit testing')
        self.params=parser.parse_args()
        if self.params.rss_url and not self.params.source_id:
            raise CustomErrors.ConfigError
        self.extracted_dbinstance = connect_db.extracted_dbinstance()
        self.aggregated_dbinstance = connect_db.aggregated_dbinstance()
        if self.params.db_connect:
            connect_db.move_last_data(extractor_db=self.extracted_dbinstance, aggregator_db=self.aggregated_dbinstance)

    def run_aggregator(self):
        """
        :return: daily article links from rss feeds (type --> list of dictionaries)
        """
        if not self.params.run_aggr:
            return 0
        else:
            logging.info("Crawler initiated")
            kwargs ={'source_id': self.params.source_id, 'rss_url': self.params.rss_url, 'aggregator_limit':
                    self.params.aggr_limit,
                     'aggregator_limit_value': self.params.aggr_limit_value, 'timeline_start_date'
                    : self.params.start_date, 'timeline_start_hour': self.params.start_hour,
                     "db_connect": self.params.db_connect}
            resp = RssFeedExtractor.getsourceobj(**kwargs)
            return resp

    def run_extractor(self):
        """
        :return:
        """
        logging.info("Extractor initiated.")
        if self.params.run_aggr:
            aggregated_data = self.run_aggregator()

        else:
            logging.info("Retrieving aggregated data from the db.")
            aggregated_data = self.aggregated_dbinstance.find({})
        for docs in aggregated_data:
            try:
                module_name = docs.get("source_id") + "_plugin"
                source_module = 'NewsPaper_Plugins.'+ module_name
                module = __import__(source_module, globals={"name": __name__})
                func = getattr(module, module_name)
                article_links = docs.get("article_links", [])
                for articles in article_links:
                    kwargs ={'source_id': docs.get("source_id"), 'source': docs.get("source"),
                             "url": articles.get("link")}
                    articles.update(func.getsourceresponse(**kwargs))
                    if self.params.db_connect:
                        self.extracted_dbinstance.insert_one(articles)
            except Exception as e:
                print(str(e))

        return 0


obj= DailyUpdates()
obj.run_extractor()
