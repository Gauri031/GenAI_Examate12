"""Command-line interface. Run from the day folder: python -m app.cli"""
from app.records import load_records, search, count_by, get_by_id


def show(r):
    print(f"[{r['id']}] G{r['guideline_no']}: {r['guideline_title']}")
    print(f"     advice: {r['key_advice']}")
    print(f"     limit : {r['number_limit'] or '-'} | group: {r['target_group']} | page: {r['page_ref']}")


def main():
    records = load_records()
    while True:
        print("\n1. Print all  2. Search keyword  3. Count per category  4. Get by id  0. Exit")
        c = input("Choose: ").strip()
        if c == "1":
            for r in records:
                show(r)
        elif c == "2":
            hits = search(records, input("Keyword: "))
            print(f"{len(hits)} result(s)")
            for r in hits:
                show(r)
        elif c == "3":
            for k, v in count_by(records, "target_group").items():
                print(f"  {k}: {v}")
        elif c == "4":
            try:
                r = get_by_id(records, int(input("Id: ")))
            except ValueError:
                r = None
            show(r) if r else print("Not found")
        elif c == "0":
            break


if __name__ == "__main__":
    main()
