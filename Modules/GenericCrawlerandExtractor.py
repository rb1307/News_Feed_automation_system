from lxml import html
from CommonFunctions import response_from_request,clean_article_body
import re


class GCA:
    def __init__(self, **kwargs):
        """
        kwargs:
                url : The url to be crawwled and extracted
                source : Newspaper source
                request_type : The request type e.g. get/post
                id_splitter: Character to split the part of url that contains article id
                extractor_configs : params to extract the element by extracttion type and path
        """
        self.values={}
        self.values.update(kwargs)
        url_detauls = {'url': self.values.get("url"), 'request_type': 'get'}
        self.values['response'] = response_from_request(**url_detauls)

    def return_reponse(self):
        return self.values.get("response").text

    def convertresponsetoxmltree(self):
        response = self.values.get("response")
        response_string = response.text
        xml_tree = html.fromstring(response_string)
        return xml_tree

    def convertstringtojson(self):
        pass

    def extractarticlebody_xml(self):
        xpath = self.values.get("extractor_configs", {}).get("xpath", {}).get("article_body", None)
        if xpath is None:
            return
        else:
            xml_tree = self.convertresponsetoxmltree()
            article_body = xml_tree.xpath(xpath)
            article_body = clean_article_body(body_list=article_body)
            return article_body

    def extractarticlebody_json(self):
        pass

    def extractarticlebody_regex(self):
        pass

    def extractimagelink_json(self):
        pass

    def extractimagelink_xml(self):
        image_xpath = self.values.get("extractor_configs", {}).get("xpath", {}).get("img_link", None)
        if image_xpath is None:
            return None
        else:
            xml_tree=self.convertresponsetoxmltree()
            image_link = xml_tree.xpath(image_xpath)
            return image_link

    def extractimagelink_regex(self):
        pass

    def extractkeywords_xml(self):
        pass

    def extractkeywords_json(self):
        pass

    def extractkeywords_regex(self):
        keyword_regex = self.values.get("extractor_configs", {}).get("regex", {}).get("keywords", None)
        if keyword_regex is None:
            return None
        else:
            response = self.values.get("response")
            keywords = re.search(keyword_regex, response.text).group(1)
            return keywords

    def extractembedtwitterlink_regex(self):
        embeded_twitter_link = self.values.get("extractor_configs", {}).get("regex", {})\
            .get("embedded_twitter_link", '')

        return embeded_twitter_link

    def authorname_xml(self):
        pass

    def authorname_regex(self):
        pass

    def authorname_json(self):
        pass


