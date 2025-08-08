"""
The stats module provides the Stats class which handles collection and processing
of test statistics in the stress testing framework. It implements a singleton
pattern and uses multiprocessing for efficient stats collection and processing.
"""

from logging import error, getLogger, info
import traceback
from typing import Optional
from gradual.configs.phase import PhaseConfig
from multiprocessing import Event, Process, Queue
from queue import Empty
import time
from gradual.reporting.adapters.base import Adapter
from gradual.reporting.adapters.logging import LoggingAdapter


class Stats:
    """
    Singleton class for managing test statistics collection and processing.

    This class provides functionality for:
    1. Collecting test statistics in a thread-safe manner
    2. Processing statistics in a separate process
    3. Managing test timing and runtime tracking
    4. Supporting database persistence of statistics

    Attributes:
        _instance (Stats): Singleton instance of the Stats class
        stop_writing (Event): Event to signal when to stop processing stats
        stats_queue (Queue): Queue for passing stats between processes
        phase_config (PhaseConfig): Configuration for the current test phase
        test_start_time (int): Timestamp when the test started
        test_end_time (int): Timestamp when the test ended
        write_db_process (Process): Process for handling stats persistence
        run_name (str): Name of the current test run
    """

    _instance = None
    stop_writing = Event()

    def __init__(self, phase_config: PhaseConfig, run_name: str):
        """
        Initialize a new Stats instance.

        Args:
            phase_config (PhaseConfig): Configuration for the current test phase
            run_name (str): Name of the current test run
        """
        self.stats_queue: Queue = Queue()
        self.phase_config = phase_config
        self.test_start_time: int
        self.test_end_time: int
        self.write_db_process = Process(target=self.process_stats, args=())
        self.run_name = run_name

    def start_process_stats(self):
        """
        Start the process that processes the stats.
        """
        self.write_db_process.start()

    def close_process_stats(self):
        """
        Terminate the process that processes the stats.
        """
        self.write_db_process.terminate()

    def process_stats(self):
        """
        Process statistics in a separate process.

        This method runs in a separate process and:
        1. Listens to the stats queue for new statistics
        2. Processes received statistics using the provided adapters
        3. Continues until stop_writing event is set

        Note:
            The method uses a timeout of 1 second when waiting for new stats
            to allow for graceful shutdown. The timeout is used to avoid
            blocking the main process.
        """
        while not self.stop_writing.is_set():
            try:
                stats, adapters = self.stats_queue.get(
                    timeout=1
                )  # wait up to 1 sec for a stat to be available
                for adapter in adapters:
                    try:
                        adapter.process_stats(stats)
                    except Exception as e:
                        error(
                            f"Stat processing failed with {adapter} with exception: {e}"
                        )
                        error(traceback.format_exc())
            except Empty:
                # queue is empty. so do nothing
                pass

    def persist_stats(self, stats, adapters: Optional[list[Adapter]] = None):
        """
        Add statistics to the processing queue.

        Args:
            stats: Statistics to be processed and persisted
            adapters: Adapters to be used to process the stats.
        """
        if adapters is None:
            adapters = [LoggingAdapter()]
        self.stats_queue.put((stats, adapters))

    @classmethod
    def get_stats_instance(cls):
        """
        Get the singleton instance of the Stats class.

        Returns:
            Stats: The singleton instance
        """
        return cls._instance

    def __new__(cls, *args, **kwargs):
        """
        Create or return the singleton instance.

        This method implements the singleton pattern, ensuring only one
        instance of the Stats class exists.

        Returns:
            Stats: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def current_runtime(self):
        """
        Calculate the current runtime of the test.

        Returns:
            float: Time elapsed since test start in seconds
        """
        return time.time() - self.test_start_time
