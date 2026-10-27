import sys, json
from graphify.extract import collect_files, extract
from pathlib import Path

raw = Path('graphify-out/.graphify_detect.json').read_bytes()
if raw[:2] == b'\xff\xfe':
    raw = raw[2:]
if raw[:3] == b'\xef\xbb\xbf':
    raw = raw[3:]
detect = json.loads(raw.decode('utf-16-le'))
code_files = []
for f in detect.get('files', {}).get('code', []):
    p = Path(f)
    code_files.extend(collect_files(p) if p.is_dir() else [p])

if code_files:
    result = extract(code_files, cache_root=Path('.'))
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f'AST: {len(result["nodes"])} nodes, {len(result["edges"])} edges')
else:
    Path('graphify-out/.graphify_ast.json').write_text(json.dumps({'nodes':[],'edges':[],'input_tokens':0,'output_tokens':0}, ensure_ascii=False), encoding="utf-8")
    print('No code files - skipping AST extraction')
