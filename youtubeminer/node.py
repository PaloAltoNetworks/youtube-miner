import logging
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
