import pytest
from csu.retry import retry


def test_retry_succeeds_after_transient():
    calls = {"n": 0}

    def flaky():
        calls["n"] += 1
        if calls["n"] < 3:
            raise RuntimeError("429")
        return "ok"

    assert retry(flaky, attempts=5, sleep=lambda _: None) == "ok"
    assert calls["n"] == 3


def test_retry_raises_on_nontransient():
    def boom():
        raise ValueError("nope")

    with pytest.raises(ValueError):
        retry(boom, attempts=3, is_transient=lambda e: False, sleep=lambda _: None)
