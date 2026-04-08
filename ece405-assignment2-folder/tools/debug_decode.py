from pathlib import Path
from resiliparse.parse.encoding import detect_encoding
from resiliparse.extract.html2text import extract_plain_text

p = Path('tests/fixtures/moby.html')
html_bytes = p.read_bytes()
print('len bytes', len(html_bytes))
# try utf-8
try:
    s = html_bytes.decode('utf-8')
    print('utf-8 decode ok; contains bullet:', '•' in s)
    t = extract_plain_text(s)
    print('utf-8 extracted contains bullet:', '•' in t)
except Exception as e:
    print('utf-8 decode failed', e)
# detect
enc = detect_encoding(html_bytes)
print('detected encoding:', enc)
if enc:
    try:
        s2 = html_bytes.decode(enc)
        print(f'{enc} decode ok; contains bullet:', '•' in s2)
        t2 = extract_plain_text(s2)
        print(f'{enc} extracted contains bullet:', '•' in t2)
    except Exception as e:
        print(f'{enc} decode failed', e)
