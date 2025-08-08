import pytest
from unittest.mock import Mock
from gradual.runners.iterators import RequestIterator
from gradual.configs.request import RequestConfig


@pytest.fixture
def mock_request_configs():
    """Create mock request configs for testing."""
    return [
        Mock(spec=RequestConfig, name="request1"),
        Mock(spec=RequestConfig, name="request2"),
        Mock(spec=RequestConfig, name="request3"),
    ]


@pytest.fixture
def iterator(mock_request_configs):
    return RequestIterator(request_types=mock_request_configs)


def test_iterator_initialization(mock_request_configs):
    """Test that RequestIterator initializes correctly with request configs."""
    iterator = RequestIterator(request_types=mock_request_configs)

    assert iterator.request_types == mock_request_configs
    assert iterator.request_type_index == 0
    assert iterator.current is None


def test_get_next_request(iterator, mock_request_configs):
    """Test getting next request in round-robin fashion."""
    # Get first request
    request1 = iterator.get_next_request()
    assert request1 == mock_request_configs[0]
    assert iterator.current == 0
    assert iterator.request_type_index == 1

    # Get second request
    request2 = iterator.get_next_request()
    assert request2 == mock_request_configs[1]
    assert iterator.current == 1
    assert iterator.request_type_index == 2

    # Get third request
    request3 = iterator.get_next_request()
    assert request3 == mock_request_configs[2]
    assert iterator.current == 2
    assert iterator.request_type_index == 0  # Should wrap around


def test_get_next_request_wraparound(iterator, mock_request_configs):
    """Test that iterator wraps around to beginning after last request."""
    # Get all requests
    for _ in range(len(mock_request_configs)):
        iterator.get_next_request()

    # Next request should be the first one again
    request = iterator.get_next_request()
    assert request == mock_request_configs[0]
    assert iterator.request_type_index == 1


def test_current_request_property(iterator, mock_request_configs):
    """Test current_request property behavior."""
    # Initially should be None
    assert iterator.current_request is None

    # After getting first request
    iterator.get_next_request()
    assert iterator.current_request == mock_request_configs[0]

    # After getting second request
    iterator.get_next_request()
    assert iterator.current_request == mock_request_configs[1]


def test_iterator_with_single_request():
    """Test iterator behavior with single request config."""
    single_request = Mock(spec=RequestConfig, name="single_request")
    iterator = RequestIterator(request_types=[single_request])

    # Should always return the same request
    for _ in range(3):
        request = iterator.get_next_request()
        assert request == single_request


def test_iterator_with_empty_list():
    """Test iterator behavior with empty request types list."""
    iterator = RequestIterator(request_types=[])

    with pytest.raises(IndexError):
        iterator.get_next_request()


def test_iterator_current_index_consistency(iterator, mock_request_configs):
    """Test that current index is consistent with returned requests."""
    for i in range(len(mock_request_configs)):
        request = iterator.get_next_request()
        assert request == mock_request_configs[iterator.current]


def test_iterator_multiple_cycles(iterator, mock_request_configs):
    """Test iterator behavior over multiple complete cycles."""
    num_cycles = 3
    total_requests = num_cycles * len(mock_request_configs)

    for i in range(total_requests):
        request = iterator.get_next_request()
        expected_index = i % len(mock_request_configs)
        assert request == mock_request_configs[expected_index]
