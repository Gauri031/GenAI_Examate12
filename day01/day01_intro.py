"""Day 01 - prints the PoshanGuide project card and asks the user a question."""

product = "PoshanGuide"
tagline = "Answers everyday eating questions strictly from ICMR-NIN Dietary Guidelines for Indians 2024, with page citations."
user = "A first-year hostel student at Sanjivani who eats mess food, drinks sweet chai 4 times a day and wonders about protein powder."
problem = "Students can't easily find trustworthy, cited answers on sugar, salt, oil and protein."
data_source = "ICMR-NIN DGI 2024 PDF (https://www.nin.res.in/dietaryguidelines/pdfjs/locale/DGI24thJune2024fin.pdf)"

print("=" * 60)
print(f"PROJECT CARD: {product}")
print("=" * 60)
print(f"Product     : {tagline}")
print(f"User        : {user}")
print(f"Problem     : {problem}")
print(f"Data source : {data_source}")
print("=" * 60)

name = input("What is your name? ").strip() or "Student"
print(f"\nHello {name}! Welcome to {product}.")
question = input("What is your nutrition question? ").strip()
print(f"Great question, {name}: '{question}'. I'll answer it from the guidelines in a later version.")
