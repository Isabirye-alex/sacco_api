"""Module for scripts.add_module_docstrings."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"venv", "__pycache__"}

updated_files = []

for path in ROOT.rglob("*.py"):
    if any(
        part in SKIP_DIRS or str(part).startswith(".venv")
        for part in path.parts
    ):
        continue

    text = path.read_text(encoding="utf-8")
    stripped = text.lstrip()
    if stripped.startswith('"""') or stripped.startswith("'''"):
        continue

    module_name = path.relative_to(ROOT).as_posix().replace("/", ".")[:-3]
    docstring = f'"""Module for {module_name}."""\n\n'
    path.write_text(docstring + text, encoding="utf-8")
    updated_files.append(path.relative_to(ROOT).as_posix())

print(f"Updated {len(updated_files)} files")
for file in updated_files:
    print(file)
