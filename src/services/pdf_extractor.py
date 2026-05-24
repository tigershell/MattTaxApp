import base64
import json
import anthropic


EXTRACTION_PROMPT = """You are extracting data from an Australian business tax invoice.
Return ONLY a JSON object with these exact keys:
- vendor: the company or supplier name
- invoice_date: the invoice date in YYYY-MM-DD format
- amount_aud: the total amount in AUD as a number (no currency symbol)
- ato_category: one of exactly these values: "Software & Subscriptions", "Domain & Hosting", "Legal & Professional", "Other Business Expenses"
- description: a brief description of what was purchased (max 100 chars)

If you cannot determine a value with confidence, use null.
Return only valid JSON, no explanation."""


class PDFExtractor:
    """Sends a PDF to Claude API and extracts structured expense data."""

    def __init__(self, api_key: str):
        self._client = anthropic.Anthropic(api_key=api_key)

    def extract(self, pdf_bytes: bytes) -> dict:
        """Extract expense fields from a PDF. Returns empty dict on failure."""
        try:
            encoded = base64.standard_b64encode(pdf_bytes).decode("utf-8")
            message = self._client.messages.create(
                model="claude-opus-4-7",
                max_tokens=512,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "document",
                                "source": {
                                    "type": "base64",
                                    "media_type": "application/pdf",
                                    "data": encoded,
                                },
                            },
                            {"type": "text", "text": EXTRACTION_PROMPT},
                        ],
                    }
                ],
            )
            return json.loads(message.content[0].text)
        except Exception:
            return {}
