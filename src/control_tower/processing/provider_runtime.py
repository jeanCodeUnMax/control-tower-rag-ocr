from __future__ import annotations

import random
import threading
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Any

from control_tower.config import VisionProviderConfig
from control_tower.processing.models import PageAnalysis, PageProfile, RenderedPage
from control_tower.processing.providers import PageVisionProvider, ProviderHTTPError


class CircuitOpenError(RuntimeError):
    pass


@dataclass
class ProviderStats:
    calls: int = 0
    successes: int = 0
    failures: int = 0
    retries: int = 0
    rate_limit_wait_seconds: float = 0.0
    total_latency_seconds: float = 0.0
    last_error: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return {
            "calls": self.calls,
            "successes": self.successes,
            "failures": self.failures,
            "retries": self.retries,
            "rate_limit_wait_seconds": round(self.rate_limit_wait_seconds, 3),
            "total_latency_seconds": round(self.total_latency_seconds, 3),
            "average_latency_seconds": round(
                self.total_latency_seconds / self.successes, 3
            ) if self.successes else None,
            "last_error": self.last_error,
        }


class ProviderRuntime:
    """Limiteur de débit, retries et circuit breaker pour un provider synchrone."""

    def __init__(self, provider: PageVisionProvider, config: VisionProviderConfig) -> None:
        self.provider = provider
        self.config = config
        self.semaphore = threading.BoundedSemaphore(config.max_concurrency)
        self.rate_lock = threading.Lock()
        self.request_times: deque[float] = deque()
        self.state_lock = threading.Lock()
        self.consecutive_failures = 0
        self.open_until = 0.0
        self.stats = ProviderStats()

    @property
    def name(self) -> str:
        return self.provider.name

    @property
    def estimated_cost_per_page_usd(self) -> float:
        return self.provider.estimated_cost_per_page_usd

    def call(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis:
        with self.state_lock:
            if time.monotonic() < self.open_until:
                raise CircuitOpenError(
                    f"Circuit {self.name} ouvert jusqu'à {self.open_until:.2f}."
                )

        last_error: Exception | None = None
        for attempt in range(self.config.max_retries + 1):
            if attempt:
                self.stats.retries += 1
            wait = self._wait_for_rate_slot()
            self.stats.rate_limit_wait_seconds += wait
            started = time.monotonic()
            self.stats.calls += 1
            try:
                with self.semaphore:
                    result = self.provider.analyze(page, profile)
                self.stats.successes += 1
                self.stats.total_latency_seconds += time.monotonic() - started
                with self.state_lock:
                    self.consecutive_failures = 0
                    self.open_until = 0.0
                return result
            except Exception as exc:
                self.stats.failures += 1
                self.stats.last_error = str(exc)
                self.stats.total_latency_seconds += time.monotonic() - started
                last_error = exc
                retryable = self._is_retryable(exc)
                with self.state_lock:
                    self.consecutive_failures += 1
                    if self.consecutive_failures >= self.config.circuit_breaker_failures:
                        self.open_until = (
                            time.monotonic() + self.config.circuit_breaker_cooldown_seconds
                        )
                if not retryable or attempt >= self.config.max_retries:
                    break
                delay = self._retry_delay(attempt, exc)
                time.sleep(delay)
        assert last_error is not None
        raise last_error

    def report(self) -> dict[str, Any]:
        with self.state_lock:
            circuit_open = time.monotonic() < self.open_until
        return {
            "name": self.name,
            "model": self.config.model,
            "enabled": self.config.enabled,
            "max_concurrency": self.config.max_concurrency,
            "requests_per_minute": self.config.requests_per_minute,
            "estimated_cost_per_page_usd": self.estimated_cost_per_page_usd,
            "circuit_open": circuit_open,
            "stats": self.stats.as_dict(),
        }

    def _wait_for_rate_slot(self) -> float:
        started = time.monotonic()
        while True:
            with self.rate_lock:
                now = time.monotonic()
                while self.request_times and now - self.request_times[0] >= 60.0:
                    self.request_times.popleft()
                if len(self.request_times) < self.config.requests_per_minute:
                    self.request_times.append(now)
                    return time.monotonic() - started
                wait = max(0.01, 60.0 - (now - self.request_times[0]))
            time.sleep(min(wait, 1.0))

    def _retry_delay(self, attempt: int, exc: Exception) -> float:
        if isinstance(exc, ProviderHTTPError) and exc.retry_after is not None:
            return min(exc.retry_after, self.config.backoff_max_seconds)
        exponential = self.config.backoff_base_seconds * (2 ** attempt)
        jitter = random.uniform(0.0, max(0.05, exponential * 0.25))
        return min(exponential + jitter, self.config.backoff_max_seconds)

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        if isinstance(exc, CircuitOpenError):
            return False
        if isinstance(exc, ProviderHTTPError):
            return exc.retryable or exc.status_code is None
        return isinstance(exc, (TimeoutError, ConnectionError, OSError))


class BudgetTracker:
    def __init__(self, maximum_usd: float) -> None:
        self.maximum_usd = maximum_usd
        self.spent_usd = 0.0
        self.lock = threading.Lock()

    def reserve(self, amount: float) -> bool:
        with self.lock:
            if self.spent_usd + amount > self.maximum_usd:
                return False
            self.spent_usd += amount
            return True

    def release(self, amount: float) -> None:
        with self.lock:
            self.spent_usd = max(0.0, self.spent_usd - amount)

    def report(self) -> dict[str, float]:
        with self.lock:
            return {
                "maximum_usd": round(self.maximum_usd, 6),
                "estimated_spent_usd": round(self.spent_usd, 6),
                "remaining_usd": round(max(0.0, self.maximum_usd - self.spent_usd), 6),
            }
