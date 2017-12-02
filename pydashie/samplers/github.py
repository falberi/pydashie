from pydashie.dashie_sampler import DashieSampler

from pydashie.config import github
import requests

class ContributorsSampler(DashieSampler):
    def __init__(self, *args, **kwargs):
        DashieSampler.__init__(self, *args, **kwargs)
        self.url = github['url'] + github['repo'] + '/stats/contributors'

    def name(self):
        return 'contributors'

    def sample(self):
        try:
            r = requests.get(self.url, verify=github['verify'], auth=github['auth'])
            assert r.status_code == 200
            entries = r.json()
            items = [{'label': entry['author']['login'], 'value': entry['total']} for entry in entries]
            items.sort(key=lambda x: x['value'], reverse=True)
        except:
            return None
        return {'items': items[:10]}

class ParticipationSampler(DashieSampler):
    def __init__(self, *args, **kwargs):
        DashieSampler.__init__(self, *args, **kwargs)
        self.url = github['url'] + github['repo'] + '/stats/participation'
        self.verify = False

    def name(self):
        return 'participation'

    def sample(self):
        try:
            r = requests.get(self.url, verify=github['verify'], auth=github['auth'])
            assert r.status_code == 200
            json = r.json()
            values = json['all'] # The array order is oldest week (index 0) to most recent week
            items = [{'x': idx, 'y': val} for idx, val in enumerate(values)]
        except:
            return None
        return {'points': list(items)}

class CommentsSampler(DashieSampler):
    def __init__(self, *args, **kwargs):
        DashieSampler.__init__(self, *args, **kwargs)
        self.url = github['url'] + github['repo'] + '/issues/comments'
        self.verify = False

    def name(self):
        return 'comments'

    def sample(self):
        try:
            r = requests.get(self.url, verify=github['verify'], auth=github['auth'])
            assert r.status_code == 200
            entries = r.json()
            comments = [{'name': entry['user']['login'], 'avatar': entry['user']['avatar_url'], 'quote': entry['body']} for entry in entries]
        except:
            return None
        return {'comments':comments}
