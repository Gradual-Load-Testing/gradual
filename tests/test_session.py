import pytest
from unittest.mock import Mock, patch
from gradual.runners.session import HTTPSession
from requests.adapters import HTTPAdapter


@pytest.fixture
def session():
    return HTTPSession(pool_connections=10, pool_maxsize=20)


def test_session_initialization():
    """Test that HTTPSession initializes correctly with pool settings."""
    session = HTTPSession(pool_connections=10, pool_maxsize=20)

    assert isinstance(session.adapter, HTTPAdapter)
    assert session.adapter._pool_connections == 10
    assert session.adapter._pool_maxsize == 20


def test_session_mounts():
    """Test that session mounts adapters for both HTTP and HTTPS."""
    session = HTTPSession(pool_connections=10, pool_maxsize=20)

    assert session.adapters["http://"] is session.adapter
    assert session.adapters["https://"] is session.adapter


def test_session_close():
    """Test that session close properly cleans up resources."""
    with patch.object(HTTPAdapter, "close") as mock_close:
        session = HTTPSession(pool_connections=10, pool_maxsize=20)
        session.close()

        mock_close.assert_called_once()


def test_session_inheritance():
    """Test that HTTPSession properly inherits from requests.Session."""
    session = HTTPSession(pool_connections=10, pool_maxsize=20)

    from requests import Session

    assert isinstance(session, Session)


def test_session_pool_limits():
    """Test that pool limits are properly enforced."""
    session = HTTPSession(pool_connections=5, pool_maxsize=10)

    assert session.adapter._pool_connections <= 5
    assert session.adapter._pool_maxsize <= 10


def test_session_adapter_reuse():
    """Test that the same adapter is used for both HTTP and HTTPS."""
    session = HTTPSession(pool_connections=10, pool_maxsize=20)

    assert session.adapters["http://"] is session.adapters["https://"]


def test_session_with_additional_args():
    """Test session initialization with additional arguments."""
    session = HTTPSession(pool_connections=10, pool_maxsize=20)
    session.headers.update({"User-Agent": "Test"})
    assert session.headers["User-Agent"] == "Test"


def test_session_close_multiple_times():
    """Test that closing session multiple times is safe."""
    with patch.object(HTTPAdapter, "close") as mock_close:
        session = HTTPSession(pool_connections=10, pool_maxsize=20)
        session.close()
        session.close()

        assert mock_close.call_count == 2
