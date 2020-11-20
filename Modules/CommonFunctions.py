import feedparser
import pytz
import logging
import requests
import dateutil.parser
from datetime import datetime, timedelta
from requests.models import Response
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

utc = pytz.UTC
HEADERS= {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko)'
        ' Chrome/77.0.3865.90 Safari/537.36'}


"""
def geturlresponse(input_url=None, request_type='get'):
    url_details = {'url': input_url, 'request_type': request_type}
    url_response = response_from_request(**url_details)
    return url_response

"""


def parserssfeedresponse(feed=None, feed_language='en'):
    if feed_language=='en':
        response = dict(feedparser.parse(feed))
        response_statuscode = response.get('status')
        if response_statuscode != 200:
            logging.warning("Feed :" + str(feed) + ". Error in retrieving data using feedparser due to status code " +
                         str(response_statuscode) + ". Check link")
            dummy_response = {'status': response_statuscode, 'entries': [], feed: response.get('feed')}
            return dummy_response
        else:
            return response
    else:
        url_response=(response_from_request(**{'url': feed, 'request_type': 'get', 'headers': HEADERS})).text
        response = dict(feedparser.parse(url_response))
        return response


def extractrssresponse(response=None, timeline_start_date=1, timeline_start_hour=0):
    feed_data=response.get("feed", {})
    metadata = {'feed_title': feed_data.get("title", ''), 'response_language': feed_data.get('language', None)}
    stories = response.get("entries")
    article_links =[]
    for each_story in stories:
        story_details ={}
        story_date_time = convertstrtodatetime(datetime_str=each_story.get("published"),
                                          date_time_format='%a, %d %b %Y %H:%M:%S +0530')
        if checkifdatetime_within_timelinelimit(input_date_time=story_date_time,
                                                timeline_days=timeline_start_date, timeline_hour=timeline_start_hour):
            story_details['title'] = each_story.get("title", None)
            story_details['published_date'] = str(story_date_time)
            story_details['summary'] = each_story.get("summary", None)
            story_details['article_body'] = each_story.get("story", None)
            story_details['link']=each_story.get('link', '')
            article_links.append(story_details)
        else:
            break
    feed_details ={'metadata': metadata, 'article_links': article_links}
    return feed_details


def checkifdatetime_within_timelinelimit(input_date_time=None, timeline_days=0, timeline_hour=0, timeline_min=0):
    timeline_days = timedelta(days=timeline_days)
    timeline= datetime.now().replace(hour=timeline_hour, minute=timeline_min)
    date_time_limit = (timeline - timeline_days)
    # logging.info("The cut off time for  is " + str(date_time_limit))
    if input_date_time.replace(tzinfo=utc) >= date_time_limit.replace(tzinfo=utc):
        return True
    else:
        return False

# def get_cutoff_timeline(timeline_days=0, timeline_hour=0, timeline_min=0):


def convertstrtodatetime(datetime_str='', date_time_format=None):
    try:
        published_date_time =dateutil.parser.parse(datetime_str)
    except Exception:
        published_date_time = datetime.strptime(datetime_str, date_time_format)
    return published_date_time


def response_from_request(**kwargs):
    request_args={}
    request_args.update(kwargs)
    url_response=None
    if request_args.get("request_type") =='get':
        url_response = requests_retry().get(request_args.get("url", ''),
                                            params=request_args.get("payload", {}),
                                            headers=HEADERS)
    elif request_args.get("request_type") =='post':
        pass
    if check_request_status_code(url=request_args.get("url"), response=url_response):
        return url_response
    else:
        return create_dummy_response(response_code=url_response.status_code, error=None)


# waiting time betweet two requests = {backoff factor} * (2 ** ({number of total retries} - 1))
def requests_retry(retries=3, back_off_factor=0.3,
                   status_forcelist=(500, 502, 504)):
    session = requests.Session()
    retry=Retry(
        total=retries,
        read=retries,
        connect=retries,
        redirect=retries-1,
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
    dummy_response.error_type=error
    print("****")
    return dummy_response


def clean_article_body(body_list=None):
    if type(body_list) is list:
        body_list = ''.join(body_list)
        return body_list


def get_current_time_string():
    current_date_time = datetime.now()
    date = current_date_time.strftime("%m/%d/%Y")
    time = current_date_time.strftime("%H:%M")
    date_time = {"current_date": date, "current_time": time }

    return date_time