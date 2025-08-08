import logging
from gradual.reporting.adapters.base import Adapter
from gradual.reporting.logger import size_based_logger


class LoggingAdapter(Adapter):
    """
    Adapter that logs the stats to a file.

    Args:
        logger: The logger to use to log the stats.
        *args: Additional arguments to pass to the Adapter class.
        **kwargs: Additional keyword arguments to pass to the Adapter class.
    """

    def __init__(
        self,
        logger: logging.Logger = size_based_logger("stress_test"),
        *args,
        **kwargs,
    ):
        self.Logger = logger
        super().__init__(*args, **kwargs)

    def process_stats(self, stat_data: dict):
        self.Logger.info(list(stat_data.items()))
