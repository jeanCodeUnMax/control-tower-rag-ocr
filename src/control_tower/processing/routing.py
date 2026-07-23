from __future__ import annotations

import os
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from control_tower.config import VisionConfig, VisionProviderConfig
from control_tower.processing.models import PageAnalysis, PageProfile, RenderedPage
from control_tower.processing.provider_runtime import BudgetTracker, ProviderRuntime
from control_tower.processing.providers import PageVisionProvider, build_page_provider
from control_tower.processing.vision import LocalVisionAnalyzer, VisionAnalyzer


class RoutedVisionAnalyzer:
    """Route chaque page indépendamment vers local, cloud ou différé."""

    provider_name = "adaptive_router"

    def __init__(
        self,
        config: VisionConfig,
        providers: dict[str, PageVisionProvider] | None = None,
    ) -> None:
        self.config = config
        self.local = LocalVisionAnalyzer()
        provider_configs = {item.name: item for item in config.providers}
        self.runtimes: list[ProviderRuntime] = []
        supplied = providers or {}
        ordered_names = list(config.provider_order)
        if config.profile in {"cloud_turbo", "night_deep"}:
            ordered_names.sort(key=lambda name: name == "ollama_local")
        for name in ordered_names:
            item = provider_configs.get(name)
            if item is None or not item.enabled:
                continue
            provider = supplied.get(name) or build_page_provider(item)
            self.runtimes.append(ProviderRuntime(provider, item))
        self.budget = BudgetTracker(config.max_cost_per_document_usd)
        self.lock = threading.Lock()
        self.routes: dict[int, dict[str, Any]] = {}
        self.deferred_pages: set[int] = set()

    def analyze_batch(
        self,
        pages: list[RenderedPage],
        profiles: dict[int, PageProfile],
    ) -> list[PageAnalysis]:
        if not pages:
            return []
        workers = min(self.config.max_workers, len(pages))
        results: dict[int, PageAnalysis] = {}
        with ThreadPoolExecutor(max_workers=workers, thread_name_prefix="vision") as pool:
            futures = {
                pool.submit(self._analyze_one, page, profiles[page.page_number]): page.page_number
                for page in pages
            }
            for future in as_completed(futures):
                page_number = futures[future]
                results[page_number] = future.result()
        return [results[number] for number in sorted(results)]

    def report(self) -> dict[str, Any]:
        with self.lock:
            routes = {str(k): v for k, v in sorted(self.routes.items())}
            deferred = sorted(self.deferred_pages)
        return {
            "profile": self.config.profile,
            "provider_order": self.config.provider_order,
            "configured_provider_count": len(self.runtimes),
            "budget": self.budget.report(),
            "deferred_pages": deferred,
            "routes": routes,
            "providers": [runtime.report() for runtime in self.runtimes],
        }

    def _analyze_one(self, page: RenderedPage, profile: PageProfile) -> PageAnalysis:
        route = route_page(profile, self.config)
        if route == "local":
            return self._local(page, profile, reason="simple_page")
        if route == "deferred":
            with self.lock:
                self.deferred_pages.add(page.page_number)
            analysis = self._local(page, profile, reason="deferred_fast_profile")
            analysis.needs_multimodal_review = True
            analysis.warnings.append(
                "Analyse multimodale différée par le profil local_fast."
            )
            return analysis

        errors: list[str] = []
        for runtime in self.runtimes:
            cost = runtime.estimated_cost_per_page_usd
            if not self.budget.reserve(cost):
                errors.append(f"budget insuffisant pour {runtime.name}")
                if self.config.stop_on_budget_exceeded:
                    raise RuntimeError(
                        f"Budget vision dépassé à la page {page.page_number}."
                    )
                continue
            try:
                analysis = runtime.call(page, profile)
                analysis.raw.setdefault("routing", {})
                analysis.raw["routing"].update(
                    {
                        "decision": "cloud",
                        "selected_provider": runtime.name,
                        "profile": self.config.profile,
                        "fallback_errors": errors,
                    }
                )
                with self.lock:
                    self.routes[page.page_number] = analysis.raw["routing"]
                return analysis
            except Exception as exc:
                self.budget.release(cost)
                errors.append(f"{runtime.name}: {exc}")

        if self.config.require_provider_success:
            raise RuntimeError(
                f"Aucun provider vision n'a traité la page {page.page_number}: {errors}"
            )
        analysis = self._local(page, profile, reason="cloud_fallback")
        analysis.needs_multimodal_review = True
        analysis.warnings.extend(errors or ["Aucun provider cloud activé."])
        return analysis

    def _local(
        self,
        page: RenderedPage,
        profile: PageProfile,
        *,
        reason: str,
    ) -> PageAnalysis:
        analysis = self.local.analyze_batch([page], {page.page_number: profile})[0]
        routing = {
            "decision": "local" if reason != "deferred_fast_profile" else "deferred",
            "selected_provider": "local",
            "profile": self.config.profile,
            "reason": reason,
        }
        analysis.raw.setdefault("routing", {}).update(routing)
        with self.lock:
            self.routes[page.page_number] = routing
        return analysis


def route_page(profile: PageProfile, config: VisionConfig) -> str:
    """Décision pure utilisée par le runtime et le préflight."""
    complex_page = bool(
        profile.requires_visual_analysis
        or profile.requires_ocr
        or profile.image_count
        or profile.drawing_count
    )
    if config.profile == "local_fast":
        if complex_page and config.defer_complex_pages_in_fast_mode:
            return "deferred"
        return "local"
    if config.profile == "night_deep":
        return "cloud"
    if config.profile in {"balanced", "cloud_turbo"}:
        return "cloud" if complex_page else "local"
    return "local"


def provider_availability(config: VisionProviderConfig) -> dict[str, Any]:
    key_available = bool(
        config.allow_missing_api_key
        or (config.api_key_env and os.getenv(config.api_key_env))
    )
    return {
        "name": config.name,
        "kind": config.kind,
        "enabled": config.enabled,
        "model": config.model,
        "base_url": config.base_url,
        "api_key_env": config.api_key_env,
        "credentials_available": key_available,
        "max_concurrency": config.max_concurrency,
        "requests_per_minute": config.requests_per_minute,
        "estimated_cost_per_page_usd": config.estimated_cost_per_page_usd,
    }


def plan_routes(profiles: list[PageProfile], config: VisionConfig) -> dict[str, Any]:
    routes = {profile.page_number: route_page(profile, config) for profile in profiles}
    counts = {
        name: sum(1 for route in routes.values() if route == name)
        for name in ("local", "cloud", "deferred")
    }
    enabled = [item for item in config.providers if item.enabled]
    minimum_cloud_cost = 0.0
    cloud_costs = [item.estimated_cost_per_page_usd for item in enabled]
    if cloud_costs:
        minimum_cloud_cost = counts["cloud"] * min(cloud_costs)
    return {
        "profile": config.profile,
        "page_count": len(profiles),
        "counts": counts,
        "routes": {str(number): route for number, route in sorted(routes.items())},
        "estimated_minimum_cloud_cost_usd": round(minimum_cloud_cost, 6),
        "budget_usd": config.max_cost_per_document_usd,
        "providers": [provider_availability(item) for item in config.providers],
    }
