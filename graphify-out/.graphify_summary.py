import json
raw = open('graphify-out/.graphify_detect.json', 'rb').read()
# Quitar BOM UTF-16 LE si existe
if raw[:2] == b'\xff\xfe':
    raw = raw[2:]
# Quitar BOM UTF-8 si existe al inicio del texto real
if raw[:3] == b'\xef\xbb\xbf':
    raw = raw[3:]
text = raw.decode('utf-16-le')
# Si todavía hay BOM UTF-8 al inicio del texto
if text.startswith('\ufeff'):
    text = text[1:]
r = json.loads(text)
fc = r.get('files', {})
print(f'Corpus: {r.get("total_files",0)} files · ~{r.get("total_words",0):,} words')
for c in ('code','document','paper','image','video'):
    if fc.get(c):
        print(f'  {c}: {len(fc.get(c))} files')
if r.get('skipped_sensitive'):
    print(f'  (skipped {len(r["skipped_sensitive"])} sensitive files)')
