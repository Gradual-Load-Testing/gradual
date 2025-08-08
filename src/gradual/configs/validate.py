"""
The validate module provides utility functions for validating stress testing
configurations. It includes functions for checking minimum concurrency values
and ensuring required properties are not empty.
"""

from logging import warning

from gradual.exceptions import InvalidConfigError


def validate_min_concurrency(min_concurrency, multiple):
    """
    Validate and adjust minimum concurrency value based on ramp-up mode.

    This function ensures that minimum concurrency is valid when using
    multiplication-based ramp-up. It prevents zero concurrency scenarios
    that would result in no test execution.

    Args:
        min_concurrency (int): The minimum concurrency value to validate
        multiple (bool): Whether multiplication-based ramp-up is being used

    Returns:
        int: The validated minimum concurrency value

    Note:
        If multiple is True and min_concurrency is 0, the function returns 1
        to prevent zero concurrency scenarios.
    """
    if multiple and min_concurrency == 0:
        warning(
            "You have passed ramp up multiplier with minimum concurrency as 0. This will result in 0 concurrency, making minimum concurrency as 1 "
        )
        return 1
    return min_concurrency


def assert_not_empty(prop, value, error_msg=None):
    """
    Assert that a configuration property has a non-empty value.

    This function validates that required configuration properties are provided
    and not empty. It raises an InvalidConfigError if the validation fails.

    Args:
        prop (str): Name of the property being validated
        value: Value to check for emptiness
        error_msg (str, optional): Custom error message to use

    Raises:
        InvalidConfigError: If the value is empty or None
    """
    if not value:
        InvalidConfigError(prop, error_msg)
