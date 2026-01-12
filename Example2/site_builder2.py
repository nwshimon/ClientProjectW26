import csv
from datetime import datetime
from pathlib import Path

def read_csv_after_header(csv_path: Path, header_startswith="Name,"):
    with csv_path.open(encoding="utf-8", newline="") as f:
        lines = f.read().splitlines()

    header_index = None
    for i, line in enumerate(lines):
        if line.startswith(header_startswith):
            header_index = i
            break

    if header_index is None:
        raise ValueError(f"Could not find a header line starting with: {header_startswith}")

    data_lines = lines[header_index:]
    reader = csv.DictReader(data_lines)
    return list(reader)

def safe(row, key, default="N/A"):
    v = (row.get(key) or "").strip()
    return v if v else default

def build_cards(records):
    cards = []
    for r in records:
        date = safe(r, "Date")
        meet = safe(r, "Meet Name")
        time = safe(r, "Time")
        place = safe(r, "Overall Place")
        grade = safe(r, "Grade")

        results_url = (r.get("Meet Results URL") or "").strip()
        photo = (r.get("Photo") or "").strip()

        link_html = f'<a href="{results_url}">Meet results</a>' if results_url else "<span>No results link</span>"
        photo_html = f'<img src="images/{photo}" alt="Photo for {meet}">' if photo else ""

        cards.append(f"""
<article>
  <h2>{meet}</h2>
  <p>{date}</p>

  {photo_html}

  <dl>
    <dt>Time</dt><dd>{time}</dd>
    <dt>Place</dt><dd>{place}</dd>
    <dt>Grade</dt><dd>{grade}</dd>
  </dl>

  <p>{link_html}</p>
</article>
""")
    return "\n".join(cards)

def fill(template_text, mapping):
    for k, v in mapping.items():
        template_text = template_text.replace(f"{{{{{k}}}}}", str(v))
    return template_text

def main():
    BASE_DIR = Path(__file__).resolve().parent

    csv_path = BASE_DIR / "garrett.csv"
    template_path = BASE_DIR / "template2.html"
    out_path = BASE_DIR / "cards.html"

    records = read_csv_after_header(csv_path)

    template = template_path.read_text(encoding="utf-8")
    cards_html = build_cards(records)

    out = fill(template, {
        "NAME": "Garrett Comer",
        "CARDS": cards_html,
        "GENERATED_AT": datetime.now().strftime("%b %d %Y, %I:%M %p"),
    })

    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path.name}")

if __name__ == "__main__":
    main()
