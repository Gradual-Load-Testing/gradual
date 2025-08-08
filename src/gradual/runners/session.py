"""
The session module provides the HTTPSession class which extends the requests.Session
class to provide connection pooling and reuse for HTTP requests during stress testing.
"""

from requests import Session
from requests.adapters import HTTPAdapter


class HTTPSession(Session):
    """
    Custom HTTP session class with connection pooling capabilities.
    
    This class extends requests.Session to provide efficient connection pooling
    for HTTP requests. It configures the underlying HTTPAdapter with specified
    pool sizes for both HTTP and HTTPS connections.
    
    Attributes:
        adapter (HTTPAdapter): The configured HTTP adapter with connection pooling
    """

    def __init__(self, pool_connections, pool_maxsize, *args, **kwargs):
        """
        Initialize the HTTP session with connection pooling configuration.
        
        Args:
            pool_connections (int): Number of connection pools to maintain
            pool_maxsize (int): Maximum number of connections per pool
            *args: Additional positional arguments for Session initialization
            **kwargs: Additional keyword arguments for Session initialization
        """
        super().__init__(*args, **kwargs)
        self.adapter = HTTPAdapter(
            pool_connections=pool_connections, pool_maxsize=pool_maxsize
        )
        self.mount("http://", self.adapter)
        self.mount("https://", self.adapter)

    def close(self):
        """
        Close the HTTP session and its connection pools.
        
        This method ensures proper cleanup of all connection pools and resources
        associated with this session.
        """
        self.adapter.close()
