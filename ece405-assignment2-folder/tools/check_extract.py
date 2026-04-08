from pathlib import Path
from cs336_data.extract import extract_text_from_html_bytes

p = Path('tests/fixtures/moby.html')
html_bytes = p.read_bytes()
print('len bytes', len(html_bytes))
res = extract_text_from_html_bytes(html_bytes)
print('extracted contains bullet:', '•' in (res or ''))
print('sample snippet:')
print(res.splitlines()[0])
