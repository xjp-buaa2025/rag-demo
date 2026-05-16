"""检查论文 .tex 文件的内部一致性：
  1. \includegraphics 引用的图是否存在
  2. \ref 与 \label 是否对应
  3. \cite 引用的是否在 thebibliography 里
"""
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..", "paper")
ROOT = os.path.abspath(ROOT)
os.chdir(ROOT)

texts = []
for fn in ["main.tex"] + [f"chapters/chapter{i}.tex" for i in [1, 2, 3, 4, 5, 6]]:
    if os.path.exists(fn):
        with open(fn, encoding="utf-8") as f:
            texts.append((fn, f.read()))
print(f"Loaded {len(texts)} files\n")

# 1. includegraphics
print("=== Figure references ===")
all_refs = []
for fn, t in texts:
    for m in re.finditer(r"\\includegraphics(?:\[[^\]]*\])?\{(figures/[^}]+)\}", t):
        all_refs.append((fn, m.group(1)))
miss = []
for fn, ref in all_refs:
    full = os.path.join(ROOT, ref)
    exists = os.path.exists(full)
    if not exists:
        miss.append(ref)
        print(f"  [MISSING] {ref} (in {fn})")
if not miss:
    print(f"  all {len(all_refs)} figure refs OK")
print()

# 2. label/ref
labels = set()
refs = set()
for fn, t in texts:
    labels.update(m.group(1) for m in re.finditer(r"\\label\{([^}]+)\}", t))
    refs.update(m.group(1) for m in re.finditer(r"\\ref\{([^}]+)\}", t))

print("=== Label/Ref ===")
unresolved = refs - labels
if unresolved:
    print(f"  Unresolved \\ref: {sorted(unresolved)}")
else:
    print(f"  all refs resolved ({len(refs)} refs)")
print(f"  Total labels: {len(labels)}, refs: {len(refs)}")
print()

# 3. cite/bibitem
cites = set()
bibitems = set()
for fn, t in texts:
    for m in re.finditer(r"\\cite\{([^}]+)\}", t):
        for k in m.group(1).split(","):
            cites.add(k.strip())
    bibitems.update(m.group(1) for m in re.finditer(r"\\bibitem\{([^}]+)\}", t))

print("=== Cite/BibItem ===")
unresolved_cite = cites - bibitems
if unresolved_cite:
    print(f"  Unresolved \\cite: {sorted(unresolved_cite)}")
else:
    print(f"  all cites resolved ({len(cites)} cites)")
unused_bib = bibitems - cites
print(f"  Defined but unused bibitems ({len(unused_bib)}): {sorted(unused_bib)[:5]}{'...' if len(unused_bib) > 5 else ''}")
print()

# 4. 章节字数
print("=== Per-chapter size ===")
for fn, t in texts:
    chars = len(t)
    cn_chars = len(re.findall(r"[一-鿿]", t))
    print(f"  {fn}: {chars:,} chars, {cn_chars:,} 中文字")
