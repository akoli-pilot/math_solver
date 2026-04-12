from __future__ import annotations

from dataclasses import dataclass, field

from app.config import MAX_DISPLAY_ELEMENTS
from app.services.wolfram_client import WolframClient, WolframClientError


@dataclass(slots=True)
class MathElement:
    element_id: str
    pod_id: str
    pod_title: str
    title: str
    plaintext: str
    image_source: str = ""

    @property
    def display_text(self) -> str:
        if self.plaintext:
            return self.plaintext
        return self.title


@dataclass(slots=True)
class SolverResult:
    query: str
    success: bool
    elements: list[MathElement] = field(default_factory=list)
    assumptions: list[str] = field(default_factory=list)
    did_you_mean: list[str] = field(default_factory=list)
    messages: list[str] = field(default_factory=list)


class WolframSolverModel:
    def __init__(self, client: WolframClient) -> None:
        self.client = client

    def solve(self, query: str) -> SolverResult:
        return self._execute_query(query)

    def explain(self, selected_text: str) -> SolverResult:
        explanation_query = f"step-by-step explanation for {selected_text}"
        return self._execute_query(explanation_query)

    def _execute_query(self, query: str) -> SolverResult:
        normalized_query = (query or "").strip()
        if not normalized_query:
            return SolverResult(query="", success=False, messages=["Query cannot be empty."])

        try:
            response = self.client.query(normalized_query)
        except (WolframClientError, ValueError) as exc:
            return SolverResult(query=normalized_query, success=False, messages=[str(exc)])

        elements = self._flatten_pods(response.get("pods", []))
        return SolverResult(
            query=normalized_query,
            success=bool(response.get("success")) and bool(elements),
            elements=elements,
            assumptions=list(response.get("assumptions", [])),
            did_you_mean=list(response.get("did_you_mean", [])),
            messages=list(response.get("messages", [])),
        )

    def _flatten_pods(self, pods: list[dict]) -> list[MathElement]:
        elements: list[MathElement] = []

        for pod in pods:
            pod_id = str(pod.get("id", "pod"))
            pod_title = str(pod.get("title", "Result"))
            subpods = pod.get("subpods", [])

            for index, subpod in enumerate(subpods, start=1):
                element = MathElement(
                    element_id=f"{pod_id}-{index}",
                    pod_id=pod_id,
                    pod_title=pod_title,
                    title=str(subpod.get("title", "Result") or "Result"),
                    plaintext=str(subpod.get("plaintext", "") or ""),
                    image_source=str(subpod.get("image_source", "") or ""),
                )
                elements.append(element)

                if len(elements) >= MAX_DISPLAY_ELEMENTS:
                    return elements

        return elements
