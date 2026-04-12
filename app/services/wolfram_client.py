from __future__ import annotations

import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from typing import Any

from app.config import REQUEST_TIMEOUT, WOLFRAM_ENDPOINT


class WolframClientError(Exception):
    """Raised when the Wolfram|Alpha API cannot be reached or parsed."""


class WolframClient:
    def __init__(self, app_id: str, endpoint: str = WOLFRAM_ENDPOINT) -> None:
        self.app_id = (app_id or "").strip()
        self.endpoint = endpoint

    def query(self, query_text: str) -> dict[str, Any]:
        normalized_query = (query_text or "").strip()
        if not normalized_query:
            raise ValueError("Please enter a math question before solving.")

        if not self.app_id:
            raise WolframClientError("Missing WOLFRAM_APP_ID environment variable.")

        params = {
            "appid": self.app_id,
            "input": normalized_query,
            "format": "plaintext,image",
        }
        request_url = f"{self.endpoint}?{urllib.parse.urlencode(params)}"

        try:
            with urllib.request.urlopen(request_url, timeout=REQUEST_TIMEOUT) as response:
                payload = response.read()
        except Exception as exc:  # noqa: BLE001
            raise WolframClientError(f"Wolfram API request failed: {exc}") from exc

        return self._parse_response(payload)

    def _parse_response(self, xml_payload: bytes) -> dict[str, Any]:
        try:
            root = ET.fromstring(xml_payload)
        except ET.ParseError as exc:
            raise WolframClientError(f"Invalid XML from Wolfram API: {exc}") from exc

        response: dict[str, Any] = {
            "success": root.attrib.get("success", "false") == "true",
            "pods": [],
            "assumptions": [],
            "did_you_mean": [],
            "messages": [],
        }

        for msg in root.findall("./error/msg"):
            text = (msg.text or "").strip()
            if text:
                response["messages"].append(text)

        for warning in root.findall("./warnings/warning"):
            warning_text = (warning.attrib.get("text") or "").strip()
            if warning_text:
                response["messages"].append(warning_text)

        for did_you_mean in root.findall("./didyoumeans/didyoumean"):
            suggestion = (did_you_mean.text or "").strip()
            if suggestion:
                response["did_you_mean"].append(suggestion)

        for assumption in root.findall("./assumptions/assumption"):
            word = (assumption.attrib.get("word") or "").strip()
            value_descriptions = []
            for value in assumption.findall("value"):
                desc = (value.attrib.get("desc") or "").strip()
                if desc:
                    value_descriptions.append(desc)
            if word and value_descriptions:
                response["assumptions"].append(f"{word}: {', '.join(value_descriptions)}")

        for pod in root.findall("pod"):
            pod_title = (pod.attrib.get("title") or "Untitled Pod").strip()
            pod_id = (pod.attrib.get("id") or pod_title.lower().replace(" ", "-")).strip()
            subpods = []

            for subpod in pod.findall("subpod"):
                plaintext = (subpod.findtext("plaintext") or "").strip()
                subpod_title = (subpod.attrib.get("title") or "").strip()

                image_source = ""
                image_node = subpod.find("img")
                if image_node is not None:
                    image_source = (image_node.attrib.get("src") or "").strip()

                subpods.append(
                    {
                        "title": subpod_title,
                        "plaintext": plaintext,
                        "image_source": image_source,
                    }
                )

            if subpods:
                response["pods"].append({"id": pod_id, "title": pod_title, "subpods": subpods})

        if not response["messages"] and not response["pods"] and not response["success"]:
            response["messages"].append(
                "No Wolfram result was returned. Try rephrasing your query."
            )

        return response
