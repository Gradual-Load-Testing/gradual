"""
Tests for the HTTP request functionality in the stress testing framework.
"""

import pytest
from unittest.mock import Mock, patch
from requests import Response
from gradual.runners.request.Http import HttpRequest
from gradual.runners.session import HTTPSession
from gradual.runners.iterators import RequestIterator
from gradual.configs.request import RequestConfig


def has_kerberos():
    """Check if requests_kerberos is available."""
    try:
        import requests_kerberos

        return True
    except ImportError:
        return False


@pytest.fixture
def mock_session():
    """Create a mock HTTPSession."""
    session = Mock(spec=HTTPSession)
    session.get = Mock(return_value=Mock(spec=Response))
    session.post = Mock(return_value=Mock(spec=Response))
    session.put = Mock(return_value=Mock(spec=Response))
    session.delete = Mock(return_value=Mock(spec=Response))
    session.close = Mock()
    return session


@pytest.fixture
def mock_iterator():
    """Create a mock RequestIterator."""
    iterator = Mock(spec=RequestIterator)
    iterator.get_next_request = Mock(return_value=Mock(spec=RequestConfig))
    return iterator


@pytest.fixture
def http_request(mock_session, mock_iterator):
    """Create an HttpRequest instance with mocked dependencies."""
    return HttpRequest(
        scenario_name="test_scenario",
        session=mock_session,
        run_once=True,
        iterator=mock_iterator,
    )


def test_initialization(http_request):
    """Test HttpRequest initialization."""
    assert http_request.scenario_name == "test_scenario"
    assert http_request.run_once is True
    assert http_request._kerberos_available is None
    assert http_request._kerberos_auth is None


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@pytest.mark.parametrize("auth,expected", [("kerb", True), ("none", False)])
def test_requires_kerberos(http_request, auth, expected):
    """Test Kerberos requirement check."""
    request_type = Mock(spec=RequestConfig)
    request_type.auth = auth
    assert http_request.requires_kerberos(request_type) is expected


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("requests_kerberos.HTTPKerberosAuth")
def test_kerberos_available(mock_kerberos_auth, http_request):
    """Test when Kerberos is available."""
    mock_auth = Mock()
    mock_kerberos_auth.return_value = mock_auth
    assert http_request._check_kerberos_availability() is True
    assert http_request._kerberos_available is True
    assert http_request._kerberos_auth == mock_auth
    assert http_request.get_kerberos_auth() == mock_auth


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("requests_kerberos.HTTPKerberosAuth", side_effect=ImportError)
def test_kerberos_not_available(mock_kerberos_auth, http_request):
    """Test when Kerberos is not available."""
    assert http_request._check_kerberos_availability() is False
    assert http_request._kerberos_available is False
    assert http_request._kerberos_auth is None
    assert http_request.get_kerberos_auth() is None


@pytest.mark.parametrize(
    "method,func",
    [
        ("GET", "get"),
        ("POST", "post"),
        ("PUT", "put"),
        ("DELETE", "delete"),
    ],
)
def test_send_request_valid_methods(http_request, mock_session, method, func):
    """Test sending a request with valid methods."""
    request_type = Mock(spec=RequestConfig)
    request_type.http_method = method
    req_kwargs = {"url": "http://test.com"}
    http_request.send_request(request_type, req_kwargs)
    getattr(mock_session, func).assert_called_once_with(**req_kwargs)


def test_send_request_invalid_method(http_request):
    """Test sending a request with invalid method."""
    request_type = Mock(spec=RequestConfig)
    request_type.http_method = "INVALID"
    req_kwargs = {"url": "http://test.com"}
    with pytest.raises(ValueError, match="Unsupported HTTP method"):
        http_request.send_request(request_type, req_kwargs)


def test_on_request_completion(http_request):
    """Test request completion handling."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.url = "http://test.com"
    request_type.context = {}
    request_type.expected_response_time = 1000
    response = Mock(spec=Response)
    response.status_code = 200
    params = {"iid": "test-id"}
    http_request.stats_instance = Mock()
    http_request.on_request_completion(
        request_type=request_type,
        response=response,
        response_time=500,
        start_time=1000,
        end_time=1500,
        params=params,
    )
    http_request.stats_instance.persist_stats.assert_called_once()
    call_args = http_request.stats_instance.persist_stats.call_args[0][0]
    print(call_args)
    assert call_args["request_name"] == "test_request"
    assert call_args["status_code"] == 200
    assert call_args["response_time"] == 500


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("gevent.spawn")
def test_run_with_kerberos_available(mock_spawn, http_request, mock_session):
    """Test running with Kerberos available."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.auth = "kerb"
    request_type.http_method = "GET"
    request_type.url = "http://test.com"
    request_type.params = {}
    http_request.iterator.get_next_request.return_value = request_type
    mock_auth = Mock()
    with patch("requests_kerberos.HTTPKerberosAuth", return_value=mock_auth):
        http_request.run()
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args[1]
    assert call_args["auth"] == mock_auth
    assert "X-ANTICSRF-HEADER" in call_args["headers"]
    assert "Content-type" in call_args["headers"]


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("gevent.spawn")
def test_run_with_kerberos_unavailable(mock_spawn, http_request, mock_session):
    """Test running with Kerberos unavailable."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.auth = "kerb"
    request_type.http_method = "GET"
    request_type.url = "http://test.com"
    request_type.params = {}
    http_request.iterator.get_next_request.return_value = request_type
    with patch("requests_kerberos.HTTPKerberosAuth", side_effect=ImportError):
        http_request.run()
    mock_session.get.assert_not_called()


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("gevent.spawn")
def test_run_without_kerberos(mock_spawn, http_request, mock_session):
    """Test running without Kerberos requirement."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.auth = "none"
    request_type.http_method = "GET"
    request_type.url = "http://test.com"
    request_type.params = {}
    http_request.iterator.get_next_request.return_value = request_type
    http_request.run()
    mock_session.get.assert_called_once()
    call_args = mock_session.get.call_args[1]
    assert "auth" not in call_args
    assert "X-ANTICSRF-HEADER" in call_args["headers"]
    assert "Content-type" in call_args["headers"]


def test_run_with_error(http_request, mock_session):
    """Test running with request error."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.http_method = "GET"
    request_type.url = "http://test.com"
    request_type.params = {}
    http_request.iterator.get_next_request.return_value = request_type
    mock_session.get.side_effect = Exception("Test error")
    http_request.run()
    mock_session.close.assert_called_once()


@pytest.mark.skipif(not has_kerberos(), reason="requests_kerberos not installed")
@patch("gevent.spawn")
def test_run_with_kerberos_unavailable_logs_error(
    mock_spawn, http_request, mock_session, caplog
):
    """Test that running with Kerberos unavailable logs an error and skips the request."""
    request_type = Mock(spec=RequestConfig)
    request_type.name = "test_request"
    request_type.auth = "kerb"
    request_type.http_method = "GET"
    request_type.url = "http://test.com"
    request_type.params = {}
    http_request.iterator.get_next_request.return_value = request_type
    with patch("requests_kerberos.HTTPKerberosAuth", side_effect=ImportError):
        http_request.run()
    mock_session.get.assert_not_called()
    # Assert the log message is present
    assert any("Skipping request" in record.message for record in caplog.records)
