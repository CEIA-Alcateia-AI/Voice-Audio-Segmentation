from functools import wraps
from time import perf_counter
from typing import Callable


def measure_segmentation_time(function: Callable) -> Callable:
    """
    Decorator that measures the execution time of segment_array_to_timestamps method
    and stores it on the instance for later use in manifest generation.

    The measured time is stored as _last_segmentation_time attribute on the instance.

    Args:
        function (Callable): The function to decorate (should be segment_array_to_timestamps).

    Returns:
        Callable: The wrapped function with timing measurement.
    """

    @wraps(function)
    def wrapper(self, *args, **kwargs):
        start_time = perf_counter()
        result = function(self, *args, **kwargs)
        end_time = perf_counter()

        # Store the segmentation time on the instance
        self._last_segmentation_time = end_time - start_time

        return result

    return wrapper
