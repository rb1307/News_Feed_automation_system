
def config_maps():
    maps={
        "The Hindu": "Hindu003_plugin.py",
        'Livemint': "Livemint_plugin.py",
        'Business Standard': "Business_Standard_plugin.py",
        'Times of India': "TOI002_plugin.py",
        'The New Indian Express': 'NIE008_plugin.py',
        'Dailythanthi': "DT_plugin.py",
        'Dinamani': 'DM_plugin.py',

    }
    return maps


class GetConfig:
    def __init__(self, source):
        self.source = source
        self.mappings = config_maps()

    def getconfigfile(self):
        plug_in = self.mappings.get(self.source)
        subprocess_call=['python', plug_in]
        return subprocess_call