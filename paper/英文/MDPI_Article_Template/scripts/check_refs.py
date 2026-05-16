import re
from pathlib import Path
text = Path("paper/英文/MDPI_Article_Template/main.tex").read_text(encoding="utf-8")
refs = sorted(set(re.findall(r"\\ref\{([^}]+)\}", text)))
labels = sorted(set(re.findall(r"\\label\{([^}]+)\}", text)))
broken = [r for r in refs if r not in labels]
unused = [l for l in labels if l not in refs]
print(f"refs: {len(refs)}, labels: {len(labels)}")
print(f"broken refs (no matching label): {broken}")
print(f"unused labels: {unused}")
