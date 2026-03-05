"""
Patch doble:
1. Arregla error float() con listas de comas (campos multi-valor)
2. Mejora el render de fórmulas con HTML con colores, sub/superscripts
"""
import ast, re

with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'rb') as f:
    src = f.read().decode('utf-8', errors='replace')

# ── PATCH 1: Arreglar on_calc para soportar campos multi-valor (coma/punto&coma) ──
OLD_VALS = '            vals = {k: float(v.text()) for k, v in fields.items()}\r\n            last_vals.clear(); last_vals.update(vals)'

NEW_VALS = (
    '            # Parsear campos: soporta floats simples Y listas separadas por coma o ;\r\n'
    '            def _parse_field(s):\r\n'
    '                s = s.strip()\r\n'
    '                if "," in s or ";" in s:\r\n'
    '                    sep = "," if "," in s else ";"\r\n'
    '                    parts = [x.strip() for x in s.split(sep) if x.strip()]\r\n'
    '                    # Intentar convertir cada parte a float\r\n'
    '                    parsed = []\r\n'
    '                    for p in parts:\r\n'
    '                        try: parsed.append(float(p))\r\n'
    '                        except ValueError: parsed.append(p)\r\n'
    '                    return parsed\r\n'
    '                try: return float(s)\r\n'
    '                except ValueError: return s  # dejarlo como string si no es número\r\n'
    '            vals = {k: _parse_field(v.text()) for k, v in fields.items()}\r\n'
    '            last_vals.clear(); last_vals.update(vals)'
)

if OLD_VALS in src:
    src = src.replace(OLD_VALS, NEW_VALS, 1)
    print("Patch 1 OK: multi-value field parser")
else:
    print("FAIL patch 1")
    idx = src.find('float(v.text())')
    if idx >= 0:
        print(repr(src[max(0,idx-30):idx+100]))

# ── PATCH 2: Reemplazar _render_result_html con versión mejorada con HTML fórmulas ──
OLD_RENDER = '''def _render_result_html(txt: str, accent: str = "#10b981") -> str:'''

# Find the complete function
start_idx = src.find(OLD_RENDER)
if start_idx < 0:
    print("FAIL: _render_result_html not found")
else:
    # Find end of function (next top-level def or class)
    func_end = re.search(r'\r?\ndef [a-zA-Z_]', src[start_idx+30:])
    end_idx = start_idx + 30 + (func_end.start() if func_end else 500)
    old_fn = src[start_idx:end_idx]
    print(f"Found _render_result_html ({len(old_fn)} chars)")

    NEW_RENDER = '''def _render_formula_html(txt: str, color: str = "#38bdf8") -> str:
    """Renderiza texto de fórmula con colores y sub/superscripts en HTML."""
    def _escape(s):
        return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
    def _math(line):
        line = _escape(line)
        # Subíndices: x_i → x<sub>i</sub>
        line = re.sub(r'([A-Za-z|])_([A-Za-z0-9{}]+)', r'\\1<sub>\\2</sub>', line)
        # Superíndices: x^2 → x<sup>2</sup>
        line = re.sub(r'([A-Za-z0-9)|}])\\^([0-9A-Za-z]+)', r'\\1<sup>\\2</sup>', line)
        # Negritas de constantes matemáticas
        for kw in ['GMD','GMR','GML','Ybus','ABCD','Slack','SIL']:
            line = line.replace(kw, f'<b>{kw}</b>')
        # Colorear "= valor"
        line = re.sub(r'(=\\s*)([+-]?\\d[\\d.,e+-]*)',
                      lambda m: f'<span style="color:{color};font-weight:900">{m.group(0)}</span>', line)
        return line

    lines = txt.split("\\n")
    parts = [
        f'<div style="font-family:Consolas,monospace; font-size:11px; '
        f'line-height:1.7; background:#020617; color:#94a3b8; padding:4px;">'
    ]
    for line in lines:
        stripped = line.lstrip()
        indent = len(line) - len(stripped)
        pad = "&nbsp;" * (indent * 2)
        # Headers de sección (━━)
        if "━" in line or "═" in line:
            parts.append(
                f'<div style="color:{color}; font-weight:900; font-size:10px; '
                f'letter-spacing:1px; margin:4px 0 2px 0;">{pad}{_escape(stripped)}</div>'
            )
        # Líneas de resultado (con =)
        elif "=" in stripped and not stripped.startswith("#"):
            parts.append(f'<div style="margin:1px 0;">{pad}{_math(stripped)}</div>')
        # Líneas de fórmula estructurada (empiezan con letra mayúscula y contienen paréntesis)
        elif stripped and stripped[0].isupper() and "(" in stripped:
            label_end = stripped.find(":")
            if label_end > 0:
                label = stripped[:label_end+1]
                rest  = stripped[label_end+1:]
                parts.append(
                    f'<div style="margin:1px 0;">{pad}'
                    f'<span style="color:{color}88; font-weight:700;">{_escape(label)}</span>'
                    f'<span>{_math(rest)}</span></div>'
                )
            else:
                parts.append(f'<div style="margin:1px 0;">{pad}{_math(stripped)}</div>')
        elif stripped.startswith("[") or stripped.startswith("•") or stripped.startswith("▸"):
            # Bullets / items numerados
            parts.append(
                f'<div style="margin:1px 0;color:#e2e8f0;">{pad}{_math(stripped)}</div>'
            )
        else:
            parts.append(f'<div>{pad}{_escape(stripped) if stripped else "&nbsp;"}</div>')
    parts.append("</div>")
    return "".join(parts)


def _render_result_html(txt: str, accent: str = "#10b981") -> str:
    """Renderiza el desarrollo matemático como HTML estructurado con color."""
    import re
    def _esc(s): return s.replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")

    lines = txt.split("\\n")
    html_parts = [
        f'<div style="font-family:Consolas,monospace; font-size:11.5px; '
        f'line-height:1.75; background:#050e1e; color:#e2e8f0; padding:8px 10px;">'
    ]
    for raw in lines:
        stripped = raw.lstrip()
        indent   = len(raw) - len(stripped)
        pad      = "&nbsp;" * (indent * 2)
        esc      = _esc(stripped)

        # ── Líneas divisoras (━ ═ ─) ──────────────────────────────────────────
        if any(c in stripped for c in "━═─"):
            html_parts.append(
                f'<div style="color:{accent}44; font-size:9px; \\'
                f'margin:5px 0 3px 0; letter-spacing:0.5px;">{pad}{esc}</div>'
            )
        # ── Encabezados [N] ────────────────────────────────────────────────────
        elif re.match(r'^\\[\\d+\\]', stripped):
            m = re.match(r'^(\\[\\d+\\])(.*)', stripped)
            num = m.group(1); rest = m.group(2)
            # Colorear "= numero" dentro del resto
            rest_colored = re.sub(
                r'(=\\s*)([+-]?[0-9][0-9.,e+\\-]*(?:\\s*[A-Za-z%°Ω/]+)?)',
                lambda x: (f'<span style="color:{accent};font-weight:900">{_esc(x.group(0))}</span>'),
                _esc(rest)
            )
            html_parts.append(
                f'<div style="margin:3px 0;">'
                f'<span style="color:{accent}; font-weight:900; \\'
                f'background:{accent}18; padding:0 4px; border-radius:3px;">{_esc(num)}</span>'
                f'<span style="color:#e2e8f0;">{rest_colored}</span>'
                f'</div>'
            )
        # ── Líneas con "= valor" (resultados clave) ────────────────────────────
        elif "=" in stripped and not stripped.startswith("#"):
            colored = re.sub(
                r'(=\\s*)([+-]?[0-9][0-9.,e+\\-]*(?:\\s*[A-Za-z%°Ω/pu]+)?)',
                lambda x: (f'<span style="color:{accent};font-weight:900">{_esc(x.group(0))}</span>'),
                esc
            )
            # Subscripts comunes
            colored = re.sub(r'([A-Za-z|])_([A-Za-z0-9]+)', r'\\1<sub>\\2</sub>', colored)
            colored = re.sub(r'([A-Za-z0-9)|}])\\^([0-9]+)', r'\\1<sup>\\2</sup>', colored)
            html_parts.append(f'<div style="margin:2px 0;">{pad}{colored}</div>')
        # ── Iteraciones k=N (Gauss-Seidel / Newton) ───────────────────────────
        elif re.match(r'^k=\\d+', stripped) or re.match(r'^it\\s*=?\\s*\\d+', stripped, re.I):
            html_parts.append(
                f'<div style="color:#38bdf8; font-size:10.5px; margin:1px 0;">{pad}{esc}</div>'
            )
        # ── Líneas de CONVERGENCIA / DIVERGENCIA ──────────────────────────────
        elif 'CONVERGENCIA' in stripped.upper() or 'DIVERGE' in stripped.upper():
            col2 = "#10b981" if 'CONVERGENCIA' in stripped.upper() else "#ef4444"
            html_parts.append(
                f'<div style="color:{col2}; font-weight:900; margin:4px 0; font-size:12px;">'
                f'{pad}{"✓" if col2=="#10b981" else "✗"} {esc}</div>'
            )
        # ── Texto normal ────────────────────────────────────────────────────────
        else:
            html_parts.append(f'<div style="margin:1px 0;">{pad}{esc if stripped else "&nbsp;"}</div>')

    html_parts.append("</div>")
    return "".join(html_parts)

'''

    src = src[:start_idx] + NEW_RENDER + src[end_idx:]
    print("Patch 2 OK: improved HTML formula rendering")

# also add import re at top of the _render functions if needed
if 'import re' not in src[:500]:
    src = src.replace('import numpy as np\n', 'import numpy as np\nimport re\n', 1)
    print("Added import re")

with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'wb') as f:
    f.write(src.encode('utf-8'))
print("Written.")

try:
    ast.parse(src)
    print("SYNTAX OK")
    print(f"Total lines: {src.count(chr(10))}")
except SyntaxError as e:
    lines = src.split('\n')
    for i, L in enumerate(lines[max(0,e.lineno-5):e.lineno+5], max(1,e.lineno-4)):
        marker = ">>>" if i == e.lineno else "   "
        print(f"{marker}{i}: {L[:100]}")
    print(f"SYNTAX ERROR line {e.lineno}: {e.msg}")
