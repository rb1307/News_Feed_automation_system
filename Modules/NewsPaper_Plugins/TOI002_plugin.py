from Modules import GenericCrawlerandExtractor
from Modules import InputMethods
from Modules import CommonFunctions
import json
import re

CONFIG_PATH = '/home/rb1307/Samagra Patrika/News_Feed_automation_system/Modules/NewsPaper_configs'
CONFIG_FILE = 'configs_TOI.json'


class TOI(GenericCrawlerandExtractor.GCA):
    def __init__(self, **kwargs):
        self.source_configs = {}
        self.source_configs.update(kwargs)
        config_data = InputMethods.input_json(path=CONFIG_PATH, file_name=CONFIG_FILE)
        self.source_configs['extractor_configs'] = config_data
        super().__init__(**self.source_configs)
        self.xml_tree = super().convertresponsetoxmltree()

    def getarticleidfromurl(self):
        article_id = self.source_configs.get("url").split("/articleshow/")[-1].split(".")[0]
        return article_id

    def getjsonobject(self):
        article_response = super().return_reponse()
        json_string = re.search("window.App=(.*?)</script><script>", article_response).group(1)
        json_obj = json.loads(json_string)

        return json_obj

    def extractarticlebody_json(self):
        article_id = self.getarticleidfromurl()
        json_dict = self.getjsonobject()
        story_list = json_dict.get("state", {}).get("articleshow", {}).get("data", {}).get(str(article_id), {})\
            .get("story", [])
        story =[]
        for items in story_list:
            if items.get("tn") in ['text', 'keywoard']:
                story.append(items.get("value"))
        article_body = CommonFunctions.clean_article_body(body_list=story)

        return article_body


    def extractkeywords_json(self):
        article_id = self.getarticleidfromurl()
        json_dict = self.getjsonobject()
        keywords = json_dict.get("state", {}).get("articleshow", {}).get("data", {}).get(str(article_id), {})\
            .get("kws", '')

        return keywords

    def extractimagelink_json(self):
        base_url ='https://static.toiimg.com/thumb/msid-'
        image_url =base_url +str(self.getarticleidfromurl()) + ',imgsize-162203/photo.jpg'
        return image_url


def getsourceresponse(**kwargs):
    obj = TOI(**kwargs)
    resp={'article_id': obj.getarticleidfromurl(), 'article_body': obj.extractarticlebody_xml(),
          'provided_keywords': obj.extractkeywords_json(), 'image': obj.extractimagelink_json(),
          'source_id': kwargs.get("source_id")}
    return resp
