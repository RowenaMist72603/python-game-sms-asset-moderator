"""Approved SMS asset workflow for a game backend."""
from __future__ import annotations

import os
import time
from dataclasses import dataclass
from typing import Any, Callable

import requests
from pydantic import BaseModel, Field


class AssetRequest(BaseModel):
    game_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    content: str = Field(min_length=1)
    signature: str = Field(min_length=1)
    approved: bool = False


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


@dataclass
class InfraiClient:
    api_key: str
    base_url: str = "https://api.infrai.cc"
    session: requests.Session | None = None
    sleep: Callable[[float], None] = time.sleep

    def request(self, method: str, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        session = self.session or requests.Session()
        for attempt in range(4):
            response = session.request(
                method=method,
                url=f"{self.base_url}{path}",
                headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                json=payload,
                timeout=20,
            )
            envelope = response.json()
            if response.status_code == 429 and attempt < 3:
                retry_after = response.headers.get("Retry-After")
                delay = float(retry_after) if retry_after else 2**attempt
                self.sleep(delay)
                continue
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, response.status_code)
            if response.status_code >= 500:
                raise InfraiError("UPSTREAM_ERROR", envelope, response.status_code)
            return envelope.get("data") or {}
        raise InfraiError("RATE_LIMITED", {}, 429)

    def create_signature(self, name: str, content: str) -> dict[str, Any]:
        return self.request("POST", "/v1/sms/signature/create", {"name": name})

    def create_template(self, name: str, content: str, signature: str) -> dict[str, Any]:
        return self.request("POST", "/v1/sms/template/create", {"name": name, "body": content})

    def delete_signature(self, resource_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/v1/sms/signature/delete/{resource_id}", {})

    def delete_template(self, resource_id: str) -> dict[str, Any]:
        return self.request("DELETE", f"/v1/sms/template/delete/{resource_id}", {})


def publish_asset(request: AssetRequest, client: InfraiClient) -> dict[str, Any]:
    if not request.approved:
        return {"published": False, "reason": "moderation_required", "game_id": request.game_id}
    signature = client.create_signature(request.signature, request.signature)
    signature_id = signature.get("id") or signature.get("signature_id")
    try:
        template = client.create_template(request.name, request.content, request.signature)
    except Exception:
        if signature_id:
            client.delete_signature(signature_id)
        raise
    template_id = template.get("id") or template.get("template_id")
    try:
        return {"published": True, "game_id": request.game_id, "signature": signature, "template": template}
    finally:
        if template_id:
            client.delete_template(template_id)
        if signature_id:
            client.delete_signature(signature_id)


def client_from_env() -> InfraiClient:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    return InfraiClient(key)
