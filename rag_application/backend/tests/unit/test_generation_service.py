"""Unit tests for :class:`GenerationService`."""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from services import generation_service as module_under_test
from services.generation_service import GenerationService


@dataclass
class _FakeResponse:
    text: str


class _FakeModel:
    def __init__(self, model_name: str) -> None:
        self.model_name = model_name
        self.prompts: list[str] = []

    def generate_content(self, prompt: str) -> _FakeResponse:
        self.prompts.append(prompt)
        return _FakeResponse(text=f"[{self.model_name}] {prompt[:20]}")


@pytest.fixture()
def fake_genai(monkeypatch: pytest.MonkeyPatch) -> list[_FakeModel]:
    instances: list[_FakeModel] = []

    def _factory(model_name: str) -> _FakeModel:
        model = _FakeModel(model_name)
        instances.append(model)
        return model

    monkeypatch.setattr(module_under_test.genai, "GenerativeModel", _factory)
    monkeypatch.setattr(module_under_test.genai, "configure", lambda **_: None)
    return instances


def test_generate_returns_model_response_text(fake_genai: list[_FakeModel]) -> None:
    service = GenerationService(api_key="fake", model="models/test-model")
    answer = service.generate("Tell me about apples.")

    assert answer.startswith("[models/test-model]")
    assert len(fake_genai) == 1
    assert fake_genai[0].prompts == ["Tell me about apples."]
