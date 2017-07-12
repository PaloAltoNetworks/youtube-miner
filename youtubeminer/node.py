import logging
import json

import requests
import bs4  # we use bs4 to parse the HTML page

from minemeld.ft.basepoller import BasePollerFT

LOG = logging.getLogger(__name__)


class Miner(BasePollerFT):
    def configure(self):
        super(Miner, self).configure()

        self.polling_timeout = self.config.get('polling_timeout', 20)
        self.verify_cert = self.config.get('verify_cert', True)

        self.channel_name = self.config.get('channel_name', None)
        if self.channel_name is None:
            raise ValueError('%s - channel name is required' % self.name)
        self.url = 'https://www.youtube.com/user/{}/videos'.format(
            self.channel_name
        )

    def _build_iterator(self, item):
        # builds the request and retrieves the page
        rkwargs = dict(
            stream=False,
            verify=self.verify_cert,
            timeout=self.polling_timeout
        )

        r = requests.get(
            self.url,
            **rkwargs
        )

        try:
            r.raise_for_status()
        except:
            LOG.debug('%s - exception in request: %s %s',
                      self.name, r.status_code, r.content)
            raise

        # parse the page
        html_soup = bs4.BeautifulSoup(r.content, "lxml")
        result = html_soup.find_all(
            'div',
            class_='yt-lockup-video',
            attrs={
                'data-context-item-id': True
            }
        )

        return result

    def _process_item(self, item):
        video_id = item.attrs.get('data-context-item-id', None)
        if video_id is None:
            LOG.error('%s - no data-context-item-id attribute', self.name)
            return []

        indicator = 'www.youtube.com/watch?v={}'.format(video_id)
        value = {
            'type': 'URL',
            'confidence': 100
        }

        return [[indicator, value]]


class PlaylistMiner(BasePollerFT):
    def configure(self):
        super(PlaylistMiner, self).configure()

        self.polling_timeout = self.config.get('polling_timeout', 20)
        self.verify_cert = self.config.get('verify_cert', True)

        self.playlist_id = self.config.get('playlist_id', None)
        if self.playlist_id is None:
            raise ValueError('%s - playlistID is required' % self.name)

        self.api_key = self.config.get('api_key', None)
        if self.api_key is None:
            raise ValueError('%s - API Key is required' % self.name)

        self.url = 'https://www.googleapis.com/youtube/v3/playlistItems'

    def _build_iterator(self, item):
        return self._retrieve_playlist()

    def _retrieve_playlist(self):
        rparams = {
            'playlistId': self.playlist_id,
            'key': self.api_key,
            'maxResults': '50',
            'part': 'contentDetails'
        }

        # builds the request and retrieves the page
        rkwargs = dict(
            stream=False,
            verify=self.verify_cert,
            timeout=self.polling_timeout,
            params=rparams
        )

        nextPageToken = True
        while nextPageToken:
            if isinstance(nextPageToken, str) or isinstance(nextPageToken, unicode):
                rparams['pageToken'] = nextPageToken

            r = requests.get(
                self.url,
                **rkwargs
            )

            try:
                r.raise_for_status()
            except:
                LOG.debug('%s - exception in request: %s %s', self.name, r.status_code, r.content)
                raise

            data = json.loads(r.content)
            for i in data['items']:
                yield i['contentDetails']['videoId']

            nextPageToken = data.get('nextPageToken', None)

    def _process_item(self, item):
        video_id = item
        if video_id is None:
            LOG.error('%s - no data-context-item-id attribute', self.name)
            return []

        indicator = 'www.youtube.com/watch?v={}'.format(video_id)
        value = {
            'type': 'URL',
            'confidence': 100
        }

        return [[indicator, value]]

class ChannelMiner(BasePollerFT):
    def configure(self):
        super(ChannelMiner, self).configure()

        self.polling_timeout = self.config.get('polling_timeout', 20)
        self.verify_cert = self.config.get('verify_cert', True)

        self.channel_id = self.config.get('channel_id', None)
        if self.channel_id is None:
            raise ValueError('%s - channelID is required' % self.name)

        self.api_key = self.config.get('api_key', None)
        if self.api_key is None:
            raise ValueError('%s - API Key is required' % self.name)

        self.url = 'https://www.googleapis.com/youtube/v3/search'

    def _build_iterator(self, item):
        return self._retrieve_playlist()

    def _retrieve_playlist(self):
        rparams = {
            'channelId': self.channel_id,
            'key': self.api_key,
            'maxResults': '50',
            'part': 'snippet'
        }

        # builds the request and retrieves the page
        rkwargs = dict(
            stream=False,
            verify=self.verify_cert,
            timeout=self.polling_timeout,
            params=rparams
        )

        nextPageToken = True
        while nextPageToken:
            if isinstance(nextPageToken, str) or isinstance(nextPageToken, unicode):
                rparams['pageToken'] = nextPageToken

            r = requests.get(
                self.url,
                **rkwargs
            )

            try:
                r.raise_for_status()
            except:
                LOG.debug('%s - exception in request: %s %s', self.name, r.status_code, r.content)
                raise

            data = json.loads(r.content)
            for i in data['items']:
                if i['id']['kind'] != 'youtube#video':
                    continue
                yield i['id']['videoId']

            nextPageToken = data.get('nextPageToken', None)

    def _process_item(self, item):
        video_id = item
        if video_id is None:
            LOG.error('%s - no data-context-item-id attribute', self.name)
            return []

        indicator = 'www.youtube.com/watch?v={}'.format(video_id)
        value = {
            'type': 'URL',
            'confidence': 100
        }

        return [[indicator, value]]
