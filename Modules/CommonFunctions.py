import feedparser
import pytz
import re
import logging
import requests
import dateutil.parser
from datetime import datetime, timedelta
from requests.models import Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

utc = pytz.UTC
HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
                         ' Chrome/77.0.3865.90 Safari/537.36'}
default_date_time_format = '%a, %d %b %Y %H:%M:%S'


def parserssfeedresponse(feed=None, feed_language='en'):
    """
    :param feed: type-->dictionary ; rss urls with inpur details such as soure id , rss_id etc.
    :param feed_language: default = english;
    :return: raw xml response is parsed into a dictionary and returned.
    """
    if feed_language == 'en':
        response = dict(feedparser.parse(feed))
        if response.get('status') != 200:
            logging.warning("Feed :" + str(feed) + ". Error in retrieving data using feedparser due to status code " +
                            str(response.get('status')) + ". Check link")
            dummy_response = create_dummy_response(response=response)
            return dummy_response
        else:
            return response
    else:
        url_response = (response_from_request(**{'url': feed, 'request_type': 'get', 'headers': HEADERS})).text
        response = dict(feedparser.parse(url_response))
        return response


def create_dummy_response(response=None):
    """
    :param response: all response from rss urls that do not have status code 200
    :return: dummy response with emtry entry list and metadata
    """
    entries = []
    feeds = response.get('feed')
    status_code = response.get('status')
    dummy_response = {'entries': entries, 'status': status_code, 'feed': feeds}
    return dummy_response


def extractrssresponse(response=None, cut_off_date=None):
    """
    :param response: parsed xml rss response
    :param cut_off_date: The new link after a specific time of a date
    :return: type-->dictionary ; metadata and all story links before the cut off date
    """
    feed_data = response.get("feed", {})
    metadata = {'feed_title': feed_data.get("title", ''), 'response_language': feed_data.get('language', None)}
    stories = response.get("entries")
    article_links = []
    for each_story in stories:
        story_timing = each_story.get("published").split("+")[0].strip()
        story_date_time = convertstrtodatetime(datetime_str=story_timing,
                                               date_time_format=default_date_time_format)
        if checkifdatetime_within_timelinelimit(input_date_time=story_date_time, cut_off_datetime=cut_off_date):
            story_details = {'title': each_story.get("title", None), 'published_date': str(story_date_time),
                             'summary': each_story.get("summary", None), 'article_body': each_story.get("story", None),
                             'link': each_story.get('link', '')}
            article_links.append(story_details)
        else:
            break
    feed_details = {'metadata': metadata, 'article_links': article_links}
    return feed_details


def convertstrtodatetime(datetime_str='', date_time_format=None):
    """
    :param datetime_str:
    :param date_time_format:
    :return:
    """
    try:
        published_date_time = dateutil.parser.parse(datetime_str)
    except Exception as e:
        published_date_time = datetime.strptime(datetime_str, date_time_format)
    return published_date_time


def checkifdatetime_within_timelinelimit(input_date_time=None, cut_off_datetime=None):
    datetime_limit = cut_off_datetime
    if input_date_time.replace(tzinfo=utc) >= datetime_limit.replace(tzinfo=utc):
        return True
    else:
        return False


def convertdatetimetostr(date_time=None):
    return date_time


def response_from_request(**kwargs):
    request_args = {}
    request_args.update(kwargs)
    url_response = None
    if request_args.get("request_type") == 'get':
        url_response = requests_retry().get(request_args.get("url", ''),
                                            params=request_args.get("payload", {}),
                                            headers=HEADERS)
    elif request_args.get("request_type") == 'post':
        pass
    if check_request_status_code(url=request_args.get("url"), response=url_response):
        return url_response
    else:
        return create_dummy_response(response_code=url_response.status_code, error=None)


# waiting time betweet two requests = {backoff factor} * (2 ** ({number of total retries} - 1))
def requests_retry(retries=3, back_off_factor=0.3,
                   status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        redirect=retries - 1,
        backoff_factor=back_off_factor,
        status_forcelist=status_forcelist
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('http://', adapter)
    return session


def check_request_status_code(url=None, response=None):
    if response.status_code != requests.codes.ok:
        logging.warning("URL :" + str(url) + ". Error in retrieving data due to status code " +
                        str(response.status_code) + ". Check url ")
        return False
    else:
        return True


def create_dummy_response(response_code=None, error=None):
    dummy_response = Response()
    dummy_response.status_code = response_code
    dummy_response.error_type = error
    return dummy_response


def check_for_testing_flag(is_test=None):
    if is_test == 'True':
        return True
    else:
        return False


def clean_article_body(body_list=[]):
    if type(body_list) is list:
        body_list = ''.join(body_list)
    body = re.sub("[^a-zA-Z' ]+", '', body_list)
    return body


def get_current_datetime_string():
    current_date_time = datetime.now()
    date = current_date_time.strftime("%m/%d/%Y")
    time = current_date_time.strftime("%H:%M")
    current_datetime = {"current_date": date, "current_time": time}

    return current_datetime


def required_datetime(no_of_days=0, hour_of_day=0, minute_of_hour=0):
    # no_of_days :: subtract the number of days of date.
    days = timedelta(days=no_of_days)
    timeline = datetime.now().replace(hour=hour_of_day, minute=minute_of_hour)
    date_time_limit = (timeline - days)
    return date_time_limit
