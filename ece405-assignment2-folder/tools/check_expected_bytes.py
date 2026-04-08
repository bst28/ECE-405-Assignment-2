from pathlib import Path
b = Path('tests/fixtures/moby_extracted.txt').read_bytes()
print(b)
print('utf-8 decode:', b.decode('utf-8', errors='replace'))
print('contains utf-8 bullet bytes:', b'\xe2\x80\xa2' in b)
print('contains cp1252 bullet byte 0x95:', b'\x95' in b)
