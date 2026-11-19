Context passages:

{context}

User question:
{question}

Reply with ONE JSON object with exactly these keys:

{
  "answerable": true or false,
  "answer": "the answer in simple words with [n] citations after each fact. If answerable is false, write exactly: I don't know",
  "sources": [list of passage numbers you used, empty list if answerable is false]
}

Set answerable to false when the passages do not clearly contain the answer. Do not add any text outside the JSON.
