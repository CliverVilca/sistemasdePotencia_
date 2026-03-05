"""Detect and fix syntax error in wizards.py."""
import ast

with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'rb') as f:
    src = f.read().decode('utf-8', errors='replace')

# Try to parse
try:
    ast.parse(src)
    print("SYNTAX OK - no fix needed")
except SyntaxError as e:
    print(f"SYNTAX ERROR line {e.lineno}: {e.msg}")
    lines = src.split('\n')
    # Show context around the error
    start = max(0, e.lineno - 10)
    end = min(len(lines), e.lineno + 10)
    for i, L in enumerate(lines[start:end], start + 1):
        marker = ">>>" if i == e.lineno else "   "
        print(f"{marker} {i:4d}: {repr(L[:120])}")
