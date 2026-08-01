from types import SimpleNamespace

from app.services.ai.service import AIService, redact_sensitive_text


class FakeResponses:
    def __init__(self) -> None:
        self.request = None

    async def create(self, **kwargs):
        self.request = kwargs
        return SimpleNamespace(output_text="  Saran yang aman.  ")


async def test_ai_redacts_pii_and_uses_configured_responses_contract() -> None:
    responses = FakeResponses()
    service = AIService.__new__(AIService)
    service.enabled = True
    service.client = SimpleNamespace(responses=responses)
    service.model = "gpt-5.6-terra"

    answer = await service.ats_review(
        "CV saya: nama@example.com, 0812-3456-7890, NIK 3173010101010001"
    )

    assert answer == "Saran yang aman."
    assert responses.request["model"] == "gpt-5.6-terra"
    assert responses.request["reasoning"] == {"effort": "none"}
    assert responses.request["store"] is False
    user_input = responses.request["input"][1]["content"]
    assert "nama@example.com" not in user_input
    assert "0812-3456-7890" not in user_input
    assert "3173010101010001" not in user_input


def test_redaction_keeps_non_sensitive_career_context() -> None:
    value = redact_sensitive_text("Data Analyst Jakarta, pengalaman 3 tahun")
    assert value == "Data Analyst Jakarta, pengalaman 3 tahun"
