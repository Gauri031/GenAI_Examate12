User question:
{question}

Think about what the person needs, then reply with ONE JSON object with exactly these keys:

{
  "answer": "2-4 short sentences in simple language, using common Indian foods. If the question cannot be answered reliably (live local info, personal medical advice, prices), say so plainly and suggest who to ask.",
  "confidence": "high | medium | low",
  "follow_up": "one useful question to ask the user next, e.g. their child's age, or whether they are pregnant"
}

Confidence rules:
- high: well-known general nutrition fact.
- medium: depends on age, health condition or quantity that was not given.
- low: you are unsure, or the question needs live/local/personal information.

Do not add any text outside the JSON.