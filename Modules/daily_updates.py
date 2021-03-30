"""
encoding : utf-8
*******************************************
author : Romit Bhattacharyya
gmail : rbhattacharyya1307@gmail.com
*******************************************
"""
import configargparse
import RssFeedExtractor
import CustomErrors
import connect_db
import logging
import News_clustering


class DailyUpdates:
    def __init__(self):
        parser = configargparse.ArgParser(default_config_files=['configs.ini'])
        parser.add_argument('--DB', dest='DB', action='store_true', help='Connect to database')
        parser.add_argument('--no-DB', dest='DB', action='store_false', help='NO Connect to database')
        parser.add_argument('--aggregator', dest='aggregator', action='store_true', help='Run The Aggregator')
        parser.add_argument('--no-aggregator', dest='aggregator', action='store_false', help='Do not run the aggregator')
        parser.add_argument('--Test', required=False, help='Test run with a rss url')
        parser.add_argument('--Days_to_subtract', type=int, required=True, help='')
        parser.add_argument('--Hours_to_subtract', type=int, required=True, help='')
        parser.add_argument('--Minutes_to_subtract', type=int, required=True, help='')
        parser.add_argument('--rss_url', default=None, help='RSS urls to be tested.')
        parser.add_argument('--source_id', default=None, help='When RSS url is tested, source_id has to be mentioned')
        self.params = parser.parse_args()
        # self.params.db_connect=False
        # argument --rss_url should alsways be accompanied by argument --source_id
        # This can be changed to arparse line requirement
        """if self.params.Test:
            if self.params.rss_url is None and self.params.source_id is None:
                raise CustomErrors.ConfigError"""
        self.extracted_dbinstance = connect_db.extracted_dbinstance()
        self.aggregated_dbinstance = connect_db.aggregated_dbinstance()
        # print(type(self.params.DB_connect))
        if self.params.DB:
            connect_db.move_last_data(extractor_db=self.extracted_dbinstance, aggregator_db=self.aggregated_dbinstance)
        else:
            logging.warning("\tNot connecting to db.")

    def run_aggregator(self):
        """if not self.params.aggregator:
            # --run_aggr False : picks the latest aggregated files from local
            # db_cursor = self.aggregated_dbinstance.find({})
            return 0
        else:"""
        logging.info(" Generic crawler initiated.")
        kwargs = {'is_test': self.params.Test,
                  'source_id': self.params.source_id,
                  'rss_url': self.params.rss_url,
                  'aggregator_limit': 0,
                  'aggregator_limit_value': 0,
                  'timeline_start_date': self.params.Days_to_subtract,
                  'timeline_start_hour': self.params.Hours_to_subtract,
                  'timeline_start_min': self.params.Minutes_to_subtract,
                  "db_connect": self.params.DB}
        resp = RssFeedExtractor.getsourceobj(**kwargs)
        return resp

    def run_extractor(self):
        """
        :return:
        """
        logging.info("Extractor initiated.")
        if self.params.aggregator:
            aggregated_data = self.run_aggregator()

        else:
            logging.warning("\tAggregator Flag down.")
            logging.warning("\tRetrieving aggregated data from the db.")
            aggregated_data = self.aggregated_dbinstance.find({})
        logging.warning("\tDB connect is disabled")
        for docs in aggregated_data:
            try:
                module_name = docs.get("source_id") + "_plugin"
                source_module = 'NewsPaper_Plugins.' + module_name
                module = __import__(source_module, globals={"name": __name__})
                func = getattr(module, module_name)
                article_links = docs.get("article_links", [])
                for articles in article_links:
                    kwargs = {'source_id': docs.get("source_id"), 'source': docs.get("source"),
                              "url": articles.get("link")}
                    articles.update(func.getsourceresponse(**kwargs))
                    if self.params.DB:
                        self.extracted_dbinstance.insert_one(articles)

            except Exception as e:
                print(str(e))

        return 0

    def run_news_clustering(self):
        if self.params.run_aggr:
            self.run_extractor()
        else:
            News_clustering.clustering.getresponse()


obj = DailyUpdates()
obj.run_extractor()
