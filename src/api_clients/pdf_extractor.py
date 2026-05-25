import base64
import json
import logging
import anthropic

logger = logging.getLogger(__name__)

EXTRACTION_PROMPT = """You are extracting data from an Australian business tax invoice.
Return ONLY a JSON object with these exact keys:
- vendor: the company or supplier name
- invoice_date: the invoice date in YYYY-MM-DD format
- amount_original: the total amount charged as a number (no currency symbol)
- currency: the currency code, e.g. "AUD" or "USD"
- gst_amount: the GST amount as a number if shown separately, otherwise null
- ato_category: one of exactly these values: "Software & Subscriptions", "Domain & Hosting", "Legal & Professional", "Other Business Expenses"
- description: a brief description of what was purchased (max 100 chars)

If you cannot determine a value with confidence, use null.
Return only valid JSON, no explanation."""


class PDFExtractor:
    """Sends a PDF to the Claude API and extracts structured invoice data.

    Uses base64 encoding to pass the PDF as a document. Returns a dict of
    extracted fields. Always show the result to the user for review before
    saving — never auto-commit extracted data.
    """

    def __init__(self, api_key: str) -> None:
        self._client = anthropic.Anthropic(api_key=api_key)

    def extract(self, pdf_bytes: bytes) -> dict:
        """Extract invoice fields from a PDF.

        Args:
            pdf_bytes: Raw bytes of the PDF file.

        Returns:
            Dict with keys: vendor, invoice_date, amount_original, currency,
            gst_amount, ato_category, description. Any field Claude cannot
            determine will be None. Returns empty dict on total failure.
        """
        try:
            encoded = self._encode_pdf(pdf_bytes)
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
            return self._parse_response(message.content[0].text)
        except anthropic.APIError as e:
            logger.error("Anthropic API error during extraction: %s", e)
            return {}
        except Exception as e:
            logger.error("Unexpected error during PDF extraction: %s", e)
            return {}

    def _encode_pdf(self, pdf_bytes: bytes) -> str:
        """Base64-encode PDF bytes for the API request."""
        return base64.standard_b64encode(pdf_bytes).decode("utf-8")

    def _parse_response(self, text: str) -> dict:
        """Parse Claude's JSON response into a dict.

        Strips markdown code fences if Claude wraps the JSON in them.
        Returns empty dict if the response is not valid JSON.
        """
        text = text.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            logger.warning("Could not parse Claude response as JSON: %s", text[:200])
            return {}
