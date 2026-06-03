from app.services.retry import compute_backoff_seconds


def test_backoff_respects_retry_after():
    assert compute_backoff_seconds(1, retry_after=10) >= 10


def test_backoff_grows_with_attempt():
    a1 = compute_backoff_seconds(1)
    a3 = compute_backoff_seconds(3)
    assert a3 >= a1
