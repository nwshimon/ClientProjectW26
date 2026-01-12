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

def parse_date(date_str):
    s = (date_str or "").strip()
    if not s:
        return None
    try:
        return datetime.strptime(s, "%b %d %Y")
    except ValueError:
        return None

def build_items(records):
    def sort_key(r):
        d = parse_date(r.get("Date"))
        # unknown dates go last
        return (0, d) if d else (1, datetime.min)

    records_sorted = sorted(records, key=sort_key)

    items = []
    for r in records_sorted:
        date = safe(r, "Date")
        meet = safe(r, "Meet Name")
        time = safe(r, "Time")
        place = safe(r, "Overall Place")
        grade = safe(r, "Grade")
        url = (r.get("Meet Results URL") or "").strip()

        link = f'<a href="{url}">View results</a>' if url else "<span>No results link</span>"

        items.append(f"""
<li>
  <h2>{meet}</h2>
  <p>{date}</p>
  <p><strong>Time:</strong> {time} | <strong>Place:</strong> {place} | <strong>Grade:</strong> {grade}</p>
  <p>{link}</p>
</li>
""")

    return "\n".join(items)

def fill(template_text, mapping):
    for k, v in mapping.items():
        template_text = template_text.replace(f"{{{{{k}}}}}", str(v))
    return template_text

def main():
    BASE_DIR = Path(__file__).resolve().parent

    csv_path = BASE_DIR / "garrett.csv"
    template_path = BASE_DIR / "template3.html"
    out_path = BASE_DIR / "timeline.html"

    records = read_csv_after_header(csv_path)

    template = template_path.read_text(encoding="utf-8")
    items_html = build_items(records)

    out = fill(template, {
        "NAME": "Garrett Comer",
        "ITEMS": items_html,
    })

    out_path.write_text(out, encoding="utf-8")
    print(f"Wrote {out_path.name}")

if __name__ == "__main__":
    main()
