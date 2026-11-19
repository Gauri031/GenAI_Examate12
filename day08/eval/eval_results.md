# RAG Evaluation Results

## Winner table

| Config | Chunk size | Top-k | Chunks | Pass | Retrieval hit | Citation ok | Correct "I don't know" | False refusals | Avg sec/question |
|--------|-----------|-------|--------|------|---------------|-------------|------------------------|----------------|------------------|
| A **(winner)** | 400 | 3 | 20 | 14/15 (93%) | 12/12 | 12/12 | 3/3 | 0/12 | 2.4 |
| B | 700 | 5 | 10 | 14/15 (93%) | 11/12 | 11/12 | 3/3 | 0/12 | 8.2 |

**Winner: Config A** (chunk size 400, top-k 3) with 14/15 questions passed.

_Run on 2026-11-19._

## Config A (chunk size 400, top-k 3)

| ID | Question | Expected | Result | Answer | Cited sources | Pass |
|----|----------|----------|--------|--------|---------------|------|
| e01 | What should a pregnant woman eat in the second trimester? | maternal_nutrition.md | answered | She should eat small, frequent meals and add an extra snack such as a bowl of dal, a glass of milk, roasted chana, groundnuts or a fruit [1]. She should also include a variety of foods each day like roti, rice, dal, pulses, milk, curd, eggs if she eats them, green leafy vegetables, other vegetables... | maternal_nutrition.md p1, maternal_nutrition.md p1 | PASS |
| e02 | Which foods are rich in iron for a 2-year-old? | child_nutrition.md | answered | Iron‑rich foods for a 2‑year‑old include dal, green leafy vegetables, ragi, dates, eggs, and meat or fish if eaten [1]. A squeeze of lemon on the meal helps absorb iron [1]. | child_nutrition.md p1 | PASS |
| e03 | Which foods give protein to young children? | child_nutrition.md | answered | Protein foods include dal, pulses, eggs, milk, curd, paneer, soybean, groundnuts, and meat or fish if the family eats them [1]. | child_nutrition.md p1 | PASS |
| e04 | What is a good weaning food at 6 months? | infant_feeding.md | answered | Mashed dal and rice is a good weaning food at 6 months [1]. | infant_feeding.md p2 | PASS |
| e05 | Is jaggery better than sugar for anaemia? | common_foods.md | answered | Jaggery is not a good treatment for anaemia; it has only a small amount of iron and the amount eaten is too little to replace iron‑rich foods or tablets [1]. | common_foods.md p1 | PASS |
| e06 | Which nutritionist near my village is free this week? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |
| e07 | What can I give my child instead of milk if he is lactose intolerant? | child_nutrition.md | answered | Curd and buttermilk are easier to digest [1]. Other calcium sources are ragi, sesame seeds and green leafy vegetables [1]. | child_nutrition.md p2 | PASS |
| e08 | How many calories are in one roti? | common_foods.md | answered | One medium roti has about 100 kcal [1]. | common_foods.md p1 | PASS |
| e09 | Which vegetables are rich in vitamin A? | common_foods.md | answered | Drumstick leaves, spinach, other green leafy vegetables, pumpkin and carrot are rich in vitamin A [1]. | common_foods.md p2 | PASS |
| e10 | What are signs of malnutrition in a toddler? | child_nutrition.md | answered | Low weight for age, very thin arms and legs, swelling of both feet, constant tiredness, hair changes, and frequent infections or diarrhoea are warning signs of malnutrition in a toddler [1]. | child_nutrition.md p2 | PASS |
| e11 | Until what age should a baby get only breast milk? | infant_feeding.md | answered | A baby should get only breast milk for the first 6 months [1]. | infant_feeding.md p1 | PASS |
| e12 | Can I give honey to my 8-month-old baby? | infant_feeding.md | answered | No, you should not give honey to an 8-month-old baby. [1] | infant_feeding.md p2 | FAIL |
| e13 | Why should I avoid tea with meals if I have anaemia? | maternal_nutrition.md | answered | Tea reduces iron absorption, so it can make anaemia worse. Avoid drinking tea with meals to help your body absorb iron better.[1] | maternal_nutrition.md p2 | PASS |
| e14 | What is the price of tomatoes in the market today? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |
| e15 | What dose of paracetamol should I give my 3-year-old with fever? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |

## Config B (chunk size 700, top-k 5)

| ID | Question | Expected | Result | Answer | Cited sources | Pass |
|----|----------|----------|--------|--------|---------------|------|
| e01 | What should a pregnant woman eat in the second trimester? | maternal_nutrition.md | answered | She should eat a variety of foods such as roti, rice, dal, pulses, milk, curd, eggs if she eats them, green leafy vegetables, other vegetables and seasonal fruits [2]. She can have small, frequent meals and add an extra snack like a bowl of dal, a glass of milk, roasted chana, groundnuts or a fruit... | maternal_nutrition.md p1, maternal_nutrition.md p1 | PASS |
| e02 | Which foods are rich in iron for a 2-year-old? | child_nutrition.md | ERROR | ERROR: Groq error 429: {"error":{"message":"Rate limit reached for model `openai/gpt-oss-120b` in organization `org_01m7jms19veak9ha7m2t7p2e44` service tier `on_demand` on tokens per minute (TPM): Limit 8000, Used 6304, Requested 1734. Please try again in 285ms. Need more tokens? Upgrade to Dev Tier... | - | FAIL |
| e03 | Which foods give protein to young children? | child_nutrition.md | answered | Good protein foods are dal, pulses, eggs, milk, curd, paneer, soybean, groundnuts, and meat or fish if the family eats them [1]. Mixing cereals with pulses, like in khichdi or dal‑roti, also improves protein [1]. | child_nutrition.md p1 | PASS |
| e04 | What is a good weaning food at 6 months? | infant_feeding.md | answered | Mashed dal and rice is a good weaning food at 6 months. Other options include khichdi with a little ghee or oil, ragi porridge, mashed banana, mashed boiled potato or pumpkin, and well‑cooked mashed egg [1]. | infant_feeding.md p2 | PASS |
| e05 | Is jaggery better than sugar for anaemia? | common_foods.md | answered | No, jaggery is not better than sugar for anaemia. It has a small amount of iron but is still mostly sugar and not enough to treat anaemia.[1] | common_foods.md p1 | PASS |
| e06 | Which nutritionist near my village is free this week? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |
| e07 | What can I give my child instead of milk if he is lactose intolerant? | child_nutrition.md | answered | You can give curd and buttermilk, which are easier to digest, and also give ragi, sesame seeds and green leafy vegetables as calcium sources [1]. | child_nutrition.md p2 | PASS |
| e08 | How many calories are in one roti? | common_foods.md | answered | One medium roti has about 100 kcal. [1] | common_foods.md p1 | PASS |
| e09 | Which vegetables are rich in vitamin A? | common_foods.md | answered | Vegetables rich in vitamin A include drumstick leaves, spinach, other green leafy vegetables, pumpkin and carrot [1]. | common_foods.md p2 | PASS |
| e10 | What are signs of malnutrition in a toddler? | child_nutrition.md | answered | A toddler may have low weight for age, very thin arms and legs, and swelling of both feet. They may also be constantly tired, have hair changes, and get frequent infections or diarrhoea. [1] | child_nutrition.md p2 | PASS |
| e11 | Until what age should a baby get only breast milk? | infant_feeding.md | answered | Only breast milk is recommended for the first 6 months of life [1]. | infant_feeding.md p1 | PASS |
| e12 | Can I give honey to my 8-month-old baby? | infant_feeding.md | answered | No, you should not give honey to an 8‑month‑old baby. Honey can be given only after the baby is 1 year old [1]. | infant_feeding.md p2 | PASS |
| e13 | Why should I avoid tea with meals if I have anaemia? | maternal_nutrition.md | answered | Tea and coffee can lower iron absorption, so they can make anaemia worse [1]. Avoid drinking them with meals to help your body absorb the iron from foods [1]. | maternal_nutrition.md p2 | PASS |
| e14 | What is the price of tomatoes in the market today? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |
| e15 | What dose of paracetamol should I give my 3-year-old with fever? | I don't know | I don't know | I don't know. I could not find this in the PoshanGuide documents. Please ask your Anganwadi worker, ASHA worker or the nearest health centre. | - | PASS |

## How pass/fail is decided

- **Answerable question:** passes if the answer is not "I don't know", cites the expected source file, and contains at least one expected keyword.
- **Unanswerable question:** passes only if the answer is "I don't know".
- The keyword check is a rough automatic proxy. Read the answers above to double-check it.
