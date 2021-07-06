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
import json
from Modules import InputMethods
from News_clustering import clustering


class DailyUpdates:
    def __init__(self):
        parser = configargparse.ArgParser(default_config_files=['configs.ini'])
        parser.add_argument('--DB', dest='DB', action='store_true', help='Connect to database')
        parser.add_argument('--no-DB', dest='DB', action='store_false', help='NO Connect to database')
        # parser.add_argument('--DB_Name', type=str, required=True, help='Name of the db in mongo')
        parser.add_argument('--account_name', type=str, required=True, help='')
        parser.add_argument('--aggregator', dest='aggregator', action='store_true', help='Run The Aggregator')
        parser.add_argument('--no-aggregator', dest='aggregator', action='store_false',
                            help='Do not run the aggregator')
        parser.add_argument('-Test', default=False, help='Test run with a rss url')
        # parser.add_argument('--no-Test', dest='Test', action='store_false', help='Test run with a rss url')
        parser.add_argument('--Days', type=int, required=True, help='')
        parser.add_argument('--Hours', type=int, required=True, help='')
        parser.add_argument('--Minutes', type=int, required=True, help='')
        parser.add_argument('-rss_url', default=None, help='RSS urls to be tested.')
        parser.add_argument('-source_id', default=None, help='When RSS url is tested, source_id has to be mentioned')
        parser.add_argument('--clustering', dest='clustering', action='store_true', help='Run Clustering')
        parser.add_argument('--no-clustering', dest='clustering', action='store_false', help='Do not Run Clustering ')
        parser.add_argument('-local', default=False, help='Store all data in Local Machine')

        self.params = parser.parse_args()
        # argument --rss_url should always be accompanied by argument --source_id
        # This can be changed to argparse line requirement
        """if self.params.Test:
            if self.params.rss_url is None and self.params.source_id is None:
                raise CustomErrors.ConfigError"""
        """if self.params.DB:
            connect_db.move_last_data(extractor_db=self.extracted_dbinstance, aggregator_db=self.aggregated_dbinstance)
        else:
            logging.warning("\tNot connecting to db.")"""

    def run_aggregator(self):
        """if not self.params.aggregator:
            # --run_aggr False : picks the latest aggregated files from local
            # db_cursor = self.aggregated_dbinstance.find({})
            return 0
        else:"""
        kwargs = {'is_test': self.params.Test,
                  'source_id': self.params.source_id,
                  'rss_url': self.params.rss_url,
                  'aggregator_limit': 0,
                  'aggregator_limit_value': 0,
                  'timeline_start_date': self.params.Days,
                  'timeline_start_hour': self.params.Hours,
                  'timeline_start_min': self.params.Minutes,
                  "db_connect": self.params.account_name}
        resp = RssFeedExtractor.get_source_obj(**kwargs)
        return resp

    def run_extractor(self):
        aggregated_data = []
        if self.params.aggregator:
            aggregated_data = self.run_aggregator()
        else:
            # CAPTURE DATA FROM LOCAL FILE
            pass
        extracted_data = []
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
                    # print(articles)
                    extracted_data.append(articles)
                    """if self.params.DB:
                        self.extracted_dbinstance.insert_one(articles)"""

            except Exception as e:
                print(str(e))
        output_file = open('test_articles.json', 'w', encoding='utf-8')
        output_file.write("[")
        for dic in extracted_data:
            json.dump(dic, output_file)
            output_file.write(",\n")
        output_file.write("]")
        return extracted_data

    def run_news_clustering(self):
        if self.params.aggregator:
            x = self.run_extractor()
            # run the aggregator or pick up from local directory - code to be written
        else:

            x = InputMethods.input_json(path='/home/rb1307/Samagra Patrika/News_Feed_automation_system/Modules',
                                        file_name='test_articles.json')
            #print(x[0])
        clustering.getresponse(extracted_data=x)

obj = DailyUpdates()
obj.run_news_clustering()

