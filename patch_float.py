"""Patch 1 ONLY: fix multi-value field parser (the critical bug)."""
import ast

with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'rb') as f:
    src = f.read().decode('utf-8', errors='replace')

# ── Fix: float() → _parse_field() en on_calc ──────────────────────────────────
MARKER = '            vals = {k: float(v.text()) for k, v in fields.items()}\r\n            last_vals.clear(); last_vals.update(vals)'

REPLACEMENT = (
    # _parse_field helper
    '            def _parse_field(s):\r\n'
    '                s = s.strip()\r\n'
    '                if "," in s or ";" in s:\r\n'
    '                    sep = "," if "," in s else ";"\r\n'
    '                    parts = [x.strip() for x in s.split(sep) if x.strip()]\r\n'
    '                    converted = []\r\n'
    '                    for p in parts:\r\n'
    '                        try: converted.append(float(p))\r\n'
    '                        except ValueError: converted.append(p)\r\n'
    '                    return converted\r\n'
    '                try: return float(s)\r\n'
    '                except ValueError: return s\r\n'
    '            vals = {k: _parse_field(v.text()) for k, v in fields.items()}\r\n'
    '            last_vals.clear(); last_vals.update(vals)'
)

if MARKER in src:
    src = src.replace(MARKER, REPLACEMENT, 1)
    print("Patch 1 OK: _parse_field inserted")
else:
    print("FAIL: marker not found in source")
    idx = src.find('float(v.text())')
    if idx >= 0:
        print(repr(src[max(0,idx-40):idx+80]))

with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'wb') as f:
    f.write(src.encode('utf-8'))
print("Written.")

try:
    ast.parse(src)
    print("SYNTAX OK — lines:", src.count(chr(10)))
except SyntaxError as e:
    lines = src.split('\n')
    for i, L in enumerate(lines[max(0,e.lineno-4):e.lineno+4], max(1,e.lineno-3)):
        print(f"{'>>>' if i==e.lineno else '   '} {i}: {L[:100]}")
    print(f"SYNTAX ERROR: {e.msg}")
