"""检查 logo/河南 目录下哪些 logo 未被 5 个 m3u 文件引用。"""
import re
from pathlib import Path

base = Path(r'd:\00trae\SDU-IPTV-PRO')
logo_dir = base / 'logo' / '河南'
files = [
    base / 'external' / 'HNM-Unicast.m3u',
    base / 'external' / 'HNM-Unicast-lite.m3u',
    base / 'external' / 'HNT-Unicast-full.m3u',
    base / 'external' / 'HNT-Unicast.m3u',
    base / 'external' / 'HNU-Multicast.m3u',
]

all_logos = {p.stem for p in logo_dir.glob('*.png')}
referenced = set()
per_file_refs = {}
for f in files:
    text = f.read_text(encoding='utf-8')
    matches = set(re.findall(r'logo/河南/([^\"\s\)]+)\.png', text))
    referenced.update(matches)
    per_file_refs[f.name] = matches

unused = all_logos - referenced
used = all_logos & referenced

print(f'河南目录下logo总数: {len(all_logos)}')
print(f'已被5个文件引用的: {len(used)}')
print(f'未被引用的: {len(unused)}')
print(f'覆盖率: {len(used) / len(all_logos) * 100:.1f}%')
print()
print('=== 未被引用的logo ({}个) ==='.format(len(unused)))
for name in sorted(unused):
    print(f'  - {name}.png')
print()
print('=== 已被引用的logo ===')
for name in sorted(used):
    in_files = [fname for fname, refs in per_file_refs.items() if name in refs]
    print(f'  - {name}.png  (用于: {", ".join(in_files)})')
