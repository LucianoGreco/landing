#!/usr/bin/env python3
"""
generar_esquema_elementos.py
Genera esquemas parciales de fabrica-agentes en 6 archivos separados.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ====== SALIDA ======
OUTPUT_DIR = r"D:\desarrollo\1. fabrica\scripts\salida"

# ====== ROOT ======
ROOT_DIR = r"D:\desarrollo\1. fabrica"

# ====== GRUPOS DE SALIDA ======
# Cada entrada tiene:
#   "archivo"  : nombre del archivo de salida
#   "elementos": rutas relativas al root
GRUPOS = [
    {
        "archivo": "1. archivo_raiz.txt",
        "elementos": [
            "fabrica-agentes/.env",
            "fabrica-agentes/.env.example",
            "fabrica-agentes/conftest.py",
            "fabrica-agentes/manage.py",
            "fabrica-agentes/pytest.ini",
            "fabrica-agentes/README.md",
            "fabrica-agentes/requirements.txt",
        ],
    },
    {
        "archivo": "2. core.txt",
        "elementos": [
            "fabrica-agentes/core",
        ],
    },
    {
        "archivo": "3. skills.txt",
        "elementos": [
            "fabrica-agentes/skills",
        ],
    },
    {
        "archivo": "4. dashboard.txt",
        "elementos": [
            "fabrica-agentes/dashboard",
        ],
    },
    {
        "archivo": "5. agents.txt",
        "elementos": [
            "fabrica-agentes/agents",
        ],
    },
    {
        "archivo": "6. resto_archivos.txt",
        "elementos": [
            "fabrica-agentes/integrations",
            "fabrica-agentes/observability",
            "fabrica-agentes/output",
            "fabrica-agentes/projects",
            "fabrica-agentes/scripts",
            "fabrica-agentes/tests",
            "fabrica-agentes/workspace",
        ],
    },
]

# ====== FILTROS ======
IGNORE_DIRS = {
    'node_modules', '.git', '.svn', '.hg', '.idea', '.vscode', '.cache',
    'dist', 'build', 'out', 'coverage', '__pycache__',
    '$recycle.bin', 'system volume information',
    'windows', 'program files', 'program files (x86)', 'temp', 'tmp',
    '.next', 'vendor'
}
IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml',
    'thumbs.db', '.ds_store', 'desktop.ini',
}
BINARY_EXTS = {
    '.png', '.jpg', '.jpeg', '.webp', '.gif', '.bmp', '.ico',
    '.pdf', '.zip', '.rar', '.7z', '.tar', '.gz',
    '.exe', '.dll', '.mp3', '.wav', '.mp4', '.avi'
}
TEXT_EXTS = {
    '.txt', '.md', '.js', '.ts', '.jsx', '.tsx', '.json',
    '.yml', '.yaml', '.css', '.scss', '.html', '.htm',
    '.env', '.sql', '.sh', '.py', '.cjs', '.mjs'
}
MAX_PREVIEW_BYTES = 512 * 1024  # 512 KB


# ====== AUXILIARES ======

def is_ignored_dir(name):
    return name.lower() in IGNORE_DIRS

def is_ignored_file(name):
    lower = name.lower()
    if lower in IGNORE_FILES:
        return True
    if lower.endswith('.map') or lower.endswith('.old'):
        return True
    if '.hot-update.' in lower:
        return True
    return False

def is_binary(filepath):
    ext = Path(filepath).suffix.lower()
    if ext in BINARY_EXTS:
        return True
    if ext in TEXT_EXTS:
        return False
    return False

def read_file_smart(filepath):
    try:
        if is_binary(filepath):
            return '[archivo binario]'
        if str(filepath).endswith('.json'):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        return json.dumps(data[0], indent=2, ensure_ascii=False)
                    return json.dumps(data, indent=2, ensure_ascii=False)
            except:
                pass
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(MAX_PREVIEW_BYTES)
            if len(content) >= MAX_PREVIEW_BYTES:
                content += '\n\n[... contenido truncado ...]'
            return content
    except Exception as e:
        return f'[error al leer: {str(e)}]'


# ====== INDEXACIÓN COMPLETA ======

def build_full_index(scan_dir, original_root, index_prefix=''):
    index_map = {}
    try:
        entries = list(Path(scan_dir).iterdir())
        dirs  = sorted([e for e in entries if e.is_dir()  and not is_ignored_dir(e.name)],
                       key=lambda x: x.name.lower())
        files = sorted([e for e in entries if e.is_file() and not is_ignored_file(e.name)],
                       key=lambda x: x.name.lower())

        for pos, item in enumerate(dirs + files, start=1):
            num = f"{index_prefix}{pos}."
            rel = item.relative_to(original_root).as_posix()
            index_map[rel] = num
            if item.is_dir():
                index_map.update(build_full_index(item, original_root, f"{num}"))
    except Exception:
        pass
    return index_map


# ====== EXPANSIÓN DE ELEMENTOS ======

def expand_elementos(root_dir, elementos_norm):
    result = []
    seen      = set()
    seen_dirs = set()

    def add(rel_posix):
        if rel_posix not in seen:
            seen.add(rel_posix)
            result.append(rel_posix)

    def expand_dir(directory, root):
        for item in sorted(directory.rglob('*')):
            if item.is_file() and not is_ignored_file(item.name):
                parts = item.relative_to(directory).parts
                if any(is_ignored_dir(p) for p in parts):
                    continue
                add(item.relative_to(root).as_posix())

    for elem in elementos_norm:
        abs_path = Path(root_dir) / elem

        if abs_path.is_dir():
            dir_key = str(abs_path)
            if dir_key not in seen_dirs:
                seen_dirs.add(dir_key)
                expand_dir(abs_path, Path(root_dir))

        elif abs_path.is_file():
            add(elem)

        else:
            add(elem)

    return result


def build_partial_tree(root_dir, elementos_norm, index_map):
    paths_to_show = set()
    for elem in elementos_norm:
        parts = elem.split('/')
        for i in range(1, len(parts) + 1):
            paths_to_show.add('/'.join(parts[:i]))

    children_map = defaultdict(list)
    for p in sorted(paths_to_show):
        parent = p.rsplit('/', 1)[0] if '/' in p else ''
        children_map[parent].append(p)

    tree_lines = []

    def render(parent, prefix):
        children = children_map.get(parent, [])
        for i, child in enumerate(children):
            is_last     = (i == len(children) - 1)
            branch      = '└── ' if is_last else '├── '
            next_prefix = prefix + ('    ' if is_last else '│   ')
            name     = child.split('/')[-1]
            num      = index_map.get(child, '?.')
            abs_path = Path(root_dir) / child
            if abs_path.exists():
                is_dir = abs_path.is_dir()
            else:
                is_dir = '.' not in name
            icon = '📁' if is_dir else '📄'
            tree_lines.append(f"{prefix}{branch}{num} {icon} {name}")
            if is_dir:
                render(child, next_prefix)

    render('', '')
    return tree_lines


# ====== PROCESAR UN GRUPO ======

def procesar_grupo(root_dir, grupo):
    elementos_raw  = grupo.get("elementos", [])
    elementos_norm = [e.replace('\\', '/').strip('/') for e in elementos_raw]
    folder_name    = Path(root_dir).name.upper()

    lines = []
    lines.append("📁 FABRICA-AGENTES — ELEMENTOS SELECCIONADOS")
    lines.append(f"📅 Generado : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"📂 Grupo    : {grupo['archivo']}")
    lines.append("")
    lines.append('▓' * 80)
    lines.append(f"📂 {folder_name}")
    lines.append(f"   Ruta: {root_dir}")
    lines.append('▓' * 80)

    if not os.path.exists(root_dir):
        lines.append(f"❌ Directorio no encontrado: {root_dir}")
        return lines, 0

    if not elementos_norm:
        lines.append("⚠️  Sin elementos definidos para este grupo.")
        return lines, 0

    elementos_norm = expand_elementos(root_dir, elementos_norm)

    for elem in elementos_norm:
        if not (Path(root_dir) / elem).exists():
            lines.append(f"⚠️  No encontrado: {elem}")

    index_map = build_full_index(root_dir, root_dir)

    lines.append("")
    lines.extend(build_partial_tree(root_dir, elementos_norm, index_map))

    archivos = [e for e in elementos_norm if (Path(root_dir) / e).is_file()]
    for elem in archivos:
        abs_path = Path(root_dir) / elem
        num      = index_map.get(elem, '?.')
        lines.append('\n' + '=' * 80)
        lines.append(f"\n{num} 📄 {abs_path.name}")
        lines.append(f"\truta   : {abs_path}")
        lines.append(f"\tcodigo :")
        lines.append('-' * 80)
        lines.append(read_file_smart(str(abs_path)))

    return lines, len(archivos)


# ====== MAIN ======

def main():
    print("🚀 Generando esquema de elementos seleccionados (multi-archivo)...")

    if not GRUPOS:
        print("⚠️  La lista GRUPOS está vacía.")
        return

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    total_archivos = 0
    for grupo in GRUPOS:
        nombre_salida = grupo["archivo"]
        output_path   = os.path.join(OUTPUT_DIR, nombre_salida)

        lines, count = procesar_grupo(ROOT_DIR, grupo)
        final_text   = '\n'.join(lines)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(final_text)
            print(f"   ✔ {nombre_salida} → {count} archivo(s)")
        except Exception as e:
            print(f"   ❌ Error al guardar {nombre_salida}: {str(e)}")

        total_archivos += count

    print(f"\n✅ Listo. Archivos generados en: {OUTPUT_DIR}")
    print(f"📊 Total archivos procesados: {total_archivos}")


if __name__ == '__main__':
    main()