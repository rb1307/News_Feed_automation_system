INPUT_DATA_ERROR ='Failed to input data. Check file'
STATUS_CODE_ERROR = 'Page data unable to retrieve.'
EMPTYRSSFEED ="No Rss feed found for input sources."
CONFIGINPUTERROR ='Configuration error.Rss url input without source id being specified.'


class InputDataError(Exception):
    def __init__(self, message=INPUT_DATA_ERROR):
        self.message = message
        super().__init__(self.message)


class StatusCodeError(Exception):
    def __init__(self, status_code=None, message=STATUS_CODE_ERROR):
        self.message ='Status Code : ' + str(status_code) + "." + message
        super().__init__(self.message)


class NoRssFeed(Exception):
    def __init__(self, message=EMPTYRSSFEED):
        self.message = message
        super().__init__(self.message)


class ConfigError(Exception):
    def __init__(self, message=CONFIGINPUTERROR):
        self.message=message
        super().__init__(self.message)