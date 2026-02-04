def seconds_to_samples(seconds: float, sample_rate: int) -> int:
    """
    Converts seconds to sample index using rounding to avoid drift.

    Args:
        seconds (float): Time in seconds.
        sample_rate (int): Sample rate in Hz.
    Returns:
        int: Corresponding sample index.
    """
    return round(seconds * sample_rate)
