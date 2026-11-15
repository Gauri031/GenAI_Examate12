# Prompt Comparison: v1 vs v2

Both prompts use the same `prompts/system.md`. Only the task prompt differs.

- **v1** (`prompts/task_v1.md`): short, plain instruction.
- **v2** (`prompts/task_v2.md`): structured instruction with answer-length limit, confidence rules and a follow-up requirement.

## Results on my 10 questions

| # | Question | v1 answer | v1 conf. | v2 answer | v2 conf. | v2 follow_up |
|---|----------|-----------|----------|-----------|----------|--------------|
| 1 | What should a pregnant woman eat in the second trimester? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 2 | Which foods are rich in iron for a 2-year-old? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 3 | How much protein does a 10-year-old need daily? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 4 | What is a good weaning food at 6 months? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 5 | Is jaggery better than sugar for anaemia? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 6 | Which nutritionist near my village is free this week? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 7 | What can I give my child instead of milk if he is lactose intolerant? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 8 | How many calories are in one roti? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 9 | Which vegetables are cheap and rich in vitamin A? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |
| 10 | What are signs of malnutrition in a toddler? | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | ERROR: GROQ_API_KEY is missing. Add it to your .env file. | - | - |

## My analysis (EDIT: write in your own words)

- **Which prompt was better overall and why?** [EDIT]
- **How did each handle Q6 (data cannot answer)?** [EDIT]
- **Was the confidence value sensible?** [EDIT]
- **Were the follow-up questions useful?** [EDIT]
- **Which prompt I chose for /chat (default) and why:** v2 [EDIT if different]
