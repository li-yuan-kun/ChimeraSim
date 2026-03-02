"""Cost model stubs."""


def estimate_latency(cycles: int, frequency_ghz: float) -> float:
    """Estimate latency in nanoseconds from cycles and frequency."""
    if frequency_ghz <= 0:
        return float("inf")
    return cycles / frequency_ghz
