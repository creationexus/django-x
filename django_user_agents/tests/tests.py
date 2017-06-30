from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test.client import Client, RequestFactory
from django.utils import unittest

from user_agents.parsers import UserAgent
from django_user_agents.utils import get_cache_key, get_user_agent, get_and_set_user_agent
from django_user_agents.templatetags import user_agents


iphone_ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
ipad_ua_string = 'Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10'
long_ua_string = 'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1) ; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.3; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648; .NET CLR 3.5.21022; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729; .NET4.0C; .NET4.0E)'


class MiddlewareTest(unittest.TestCase):

    def test_middleware_assigns_user_agent(self):
        client = Client(HTTP_USER_AGENT=ipad_ua_string)
        response = client.get(reverse('user_agent_test'))
        self.assertIsInstance(response.context['user_agent'], UserAgent)

    def test_cache_is_set(self):
        request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get('')
        user_agent = get_user_agent(request)
        self.assertIsInstance(user_agent, UserAgent)
        self.assertIsInstance(cache.get(get_cache_key(iphone_ua_string)), UserAgent)

    def test_empty_user_agent_does_not_cause_error(self):
        request = RequestFactory().get('')
        user_agent = get_user_agent(request)
        self.assertIsInstance(user_agent, UserAgent)

    def test_get_and_set_user_agent(self):
        # Test that get_and_set_user_agent attaches ``user_agent`` to request
        request = RequestFactory().get('')
        get_and_set_user_agent(request)
        self.assertIsInstance(request.user_agent, UserAgent)

    def test_filters_can_be_loaded_in_template(self):
        client = Client(HTTP_USER_AGENT=ipad_ua_string)
        response = client.get(reverse('user_agent_test_filters'))
        self.assertEqual(response.status_code, 200)

    def test_filters(self):
        request = RequestFactory(HTTP_USER_AGENT=iphone_ua_string).get('')
        self.assertTrue(user_agents.is_mobile(request))
        self.assertTrue(user_agents.is_touch_capable(request))
        self.assertFalse(user_agents.is_tablet(request))
        self.assertFalse(user_agents.is_pc(request))
        self.assertFalse(user_agents.is_bot(request))

    def test_get_cache_key(self):
        self.assertEqual(
            get_cache_key(long_ua_string),
            'django_user_agents.c226ec488bae76c60dd68ad58f03d729',
        )
        self.assertEqual(
            get_cache_key(iphone_ua_string),
            'django_user_agents.00705b9375a0e46e966515fe90f111da',
        )
