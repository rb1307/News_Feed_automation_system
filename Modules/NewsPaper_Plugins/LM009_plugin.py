from Modules import GenericCrawlerandExtractor
from Modules import InputMethods

CONFIG_PATH = '/home/rb1307/Samagra Patrika/News_Feed_automation_system/Modules/NewsPaper_configs'
CONFIG_FILE = 'configs_livemint.json'


class LivemInt(GenericCrawlerandExtractor.GCA):
    def __init__(self, **kwargs):
        self.source_configs = {}
        self.source_configs.update(kwargs)
        config_data = InputMethods.input_json(path=CONFIG_PATH, file_name=CONFIG_FILE)
        self.source_configs['extractor_configs'] = config_data
        super().__init__(**self.source_configs)
        self.xml_tree = super().convertresponsetoxmltree()

    def getarticleidfromurl(self):
        article_id = self.source_configs.get("url").split("-")[-1].split(".html")[0]
        return article_id


def getsourceresponse(**kwargs):
    obj = LivemInt(**kwargs)
    resp = {'article_id': obj.getarticleidfromurl(), 'article_body': obj.extractarticlebody_xml(),
          'source_id': kwargs.get("source_id")}
    return resp