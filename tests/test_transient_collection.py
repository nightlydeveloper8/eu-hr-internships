import unittest
from unittest.mock import patch
from urllib.error import HTTPError

from collector.runtime import BudgetClient


class TransientCollectionTests(unittest.TestCase):
    URL = 'https://www.synergie-italia.it/sitemap-jobs.xml'

    def test_retries_503_and_timeout_with_exponential_backoff(self):
        client = BudgetClient(seconds=30, max_requests=3)
        client.retry_hosts = {'www.synergie-italia.it'}
        errors = [HTTPError(self.URL, 503, 'busy', {}, None), TimeoutError(), (b'ok', 200, self.URL)]
        with patch('collector.runtime.Client.request', side_effect=errors), patch.object(client, 'pause') as pause:
            self.assertEqual(client.request(self.URL, robots=False), (b'ok', 200, self.URL))
        self.assertEqual(client.requests, 3)
        self.assertEqual([call.args[0] for call in pause.call_args_list], [2, 4])
        self.assertEqual(client.retry_outcomes, {'http-503': 1, 'timeout': 1, 'recovered': 1})

    def test_retry_does_not_spend_an_exhausted_request_budget(self):
        client = BudgetClient(seconds=30, max_requests=1)
        client.retry_hosts = {'www.synergie-italia.it'}
        with patch('collector.runtime.Client.request', side_effect=TimeoutError), patch.object(client, 'pause') as pause:
            with self.assertRaises(TimeoutError):
                client.request(self.URL, robots=False)
        self.assertEqual(client.requests, 1)
        pause.assert_not_called()
        self.assertEqual(client.retry_outcomes, {'timeout': 1, 'exhausted': 1})
