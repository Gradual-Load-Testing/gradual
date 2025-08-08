"""
This module contains custom exceptions used throughout the stress testing framework.
These exceptions help provide clear error messages and handle specific error cases
that may occur during test configuration and execution.
"""

class InvalidConfigError(ValueError):
    """
    Exception raised when user passes invalid or missing configuration properties.
    
    This exception is used to indicate configuration errors in the stress testing framework,
    such as missing required parameters or invalid values in the configuration files.
    
    Attributes:
        prop (str, optional): The property for which the configuration is invalid or empty.
        msg (str, optional): Detailed explanation of the error. If not provided, a default
            message will be generated based on the property name.
    """

    def __init__(self, prop=None, msg=None):
        """
        Initialize the InvalidConfigError with property and message details.
        
        Args:
            prop (str, optional): The property that caused the error
            msg (str, optional): Custom error message. If not provided, a default message
                will be generated using the property name.
        """
        if not msg and prop is None:
            self.message = f"Please provide a value for {prop}"
        else:
            self.message = msg

        super().__init__(self.message)
