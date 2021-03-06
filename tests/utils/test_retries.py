"""
Copyright (c) 2020 Red Hat, Inc
All rights reserved.

This software may be modified and distributed under the terms
of the BSD license. See the LICENSE file for details.
"""

from __future__ import absolute_import, unicode_literals

import requests
from urllib3 import Retry

import pytest
from flexmock import flexmock

from atomic_reactor.constants import (HTTP_MAX_RETRIES,
                                      HTTP_REQUEST_TIMEOUT)
from atomic_reactor.utils.retries import SessionWithTimeout, get_retrying_requests_session


@pytest.mark.parametrize('timeout', [None, 0, 10])
def test_session_with_timeout(timeout):
    """
    Test that session sets default timeout if not specified
    """
    session = SessionWithTimeout()

    test_url = 'http://test.net'

    def mocked_request(method, url, **kwargs):
        assert method == 'GET'
        assert url == test_url
        assert 'timeout' in kwargs
        expected_timeout = timeout if timeout is not None else HTTP_REQUEST_TIMEOUT
        assert kwargs['timeout'] == expected_timeout

    (flexmock(requests.Session)
     .should_receive('request')
     .replace_with(mocked_request))

    if timeout is not None:
        session.get(test_url, timeout=timeout)
    else:
        session.get(test_url)


@pytest.mark.parametrize('times', [None, 0, 5])
def test_get_retrying_requests_session(times):
    """
    Test that retries are set properly for http(s):// adapters

    Most arguments are simply passed to Retry.__init__, test only basic functionality
    """
    if times is not None:
        session = get_retrying_requests_session(times=times)
    else:
        session = get_retrying_requests_session()

    http = session.adapters['http://']
    https = session.adapters['https://']

    assert isinstance(http.max_retries, Retry)
    assert isinstance(https.max_retries, Retry)

    expected_total = times if times is not None else HTTP_MAX_RETRIES
    assert http.max_retries.total == expected_total
    assert https.max_retries.total == expected_total
