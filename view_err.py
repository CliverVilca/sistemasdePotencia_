"""Show lines 85-105 of wizards.py to see exact error."""
with open('f:/New_Project/sistemasdePotencia_/app/ui/wizards.py', 'rb') as f:
    src = f.read().decode('utf-8', errors='replace')
lines = src.split('\n')
for i, L in enumerate(lines[82:110], 83):
    print(f"{i:4d}: {repr(L[:150])}")
