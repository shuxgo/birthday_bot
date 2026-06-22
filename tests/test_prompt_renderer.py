import pytest

from app.services.prompt_renderer import SafePromptRenderer


def test_prompt_renderer_replaces_known_variables():
    assert SafePromptRenderer().render("Hello {name}", {"name": "Ivan"}) == "Hello Ivan"


def test_prompt_renderer_fails_on_missing_variable():
    with pytest.raises(ValueError):
        SafePromptRenderer().render("Hello {name}", {})

