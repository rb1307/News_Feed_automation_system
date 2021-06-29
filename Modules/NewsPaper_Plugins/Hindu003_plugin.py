from Modules import GenericCrawlerandExtractor
from Modules import InputMethods
from Modules import CommonFunctions

CONFIG_PATH = '/home/hp/NFA-System/Modules/NewsPaper_configs'
CONFIG_FILE = 'configs_The Hindu.json'


class Hindu(GenericCrawlerandExtractor.GCA):
    def __init__(self, **kwargs):
        self.source_configs = {}
        self.source_configs.update(kwargs)
        config_data = InputMethods.input_json(path=CONFIG_PATH, file_name=CONFIG_FILE)
        self.source_configs['extractor_configs'] = config_data
        super().__init__(**self.source_configs)
        self.xml_tree = super().convertresponsetoxmltree()

    def getarticleidfromurl(self):
        article_id = self.source_configs.get("url").split("/article")[-1].split(".")[0]
        return article_id

    def extractarticlebody_xml(self):
        a_id = self.getarticleidfromurl()
        xpath = "//div[@id='content-body-14269002-" + str(a_id) + "']//text()"
        body = self.xml_tree.xpath(xpath)
        article_body = CommonFunctions.clean_article_body(body_list=body)
        return article_body


def getsourceresponse(**kwargs):
    obj = Hindu(**kwargs)
    resp = {'article_id': obj.getarticleidfromurl(), 'image': obj.extractimagelink_xml(),
           'provided_keywords': obj.extractkeywords_regex(), 'article_body': obj.extractarticlebody_xml(),
           'source_id': kwargs.get("source_id")}
    return resp