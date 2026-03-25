#!/usr/bin/env python3
"""
generar_esquema_elementos.py
Genera un esquema parcial de fabrica-agentes con los archivos solicitados,
conservando la numeración jerárquica del esquema completo.
Soporta múltiples ROOT_DIR en una sola salida.

Uso: editar la lista FUENTES con cada root y sus elementos deseados.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# ====== SALIDA ======
OUTPUT_FILE = r"D:\desarrollo\3. proyectos\landing\scripts\salida\project.txt"


# ====== FUENTES =====================================================
# Cada entrada tie:
#   "root"     : ruta base a indexar completa
#   "elementos": rutas relativas al root. Pueden ser:
#
#     📁 CARPETA  →  trae TODOS sus archivos (skill.py + skill_meta.json + __init__.py, etc.)
#                    "skills/cache_manager"
#
#     📄 ARCHIVO  →  trae solo ese archivo exacto
#                    "skills/cache_manager/skill_meta.json"
#
#   REGLA: si todos los archivos que necesitás están en la misma carpeta,
#          ponés solo la carpeta y listo. No repetís elementos.
# ====================================================================
FUENTES = [
    {
        "root": r"D:\desarrollo\3. proyectos",
        "elementos": [
            "landing\cafeteria-deportiva",
        ],
    },
]

# ====== FILTROS ======
IGNORE_DIRS = {""
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
    """
    Recorre TODO el directorio y devuelve:
      { ruta_relativa_posix: "N.N.N." }
    Las claves siempre son relativas a original_root (no a scan_dir).
    """
    index_map = {}
    try:
        entries = list(Path(scan_dir).iterdir())
        dirs  = sorted([e for e in entries if e.is_dir()  and not is_ignored_dir(e.name)],
                       key=lambda x: x.name.lower())
        files = sorted([e for e in entries if e.is_file() and not is_ignored_file(e.name)],
                       key=lambda x: x.name.lower())

        for pos, item in enumerate(dirs + files, start=1):
            num = f"{index_prefix}{pos}."
            rel = item.relative_to(original_root).as_posix()   # ← siempre desde el root original
            index_map[rel] = num
            if item.is_dir():
                index_map.update(build_full_index(item, original_root, f"{num}"))
    except Exception:
        pass
    return index_map



# ====== EXPANSIÓN DE ELEMENTOS ======

def expand_elementos(root_dir, elementos_norm):
    """
    Reglas de expansión:
      - Elemento es una CARPETA  → expande TODOS sus archivos (recursivo, sin duplicados).
      - Elemento es un ARCHIVO   → incluye SOLO ese archivo exacto.
      - Elemento no existe       → lo conserva para mostrar el warning.
    """
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
            # 📁 CARPETA → expandir todo su contenido (una sola vez por carpeta)
            dir_key = str(abs_path)
            if dir_key not in seen_dirs:
                seen_dirs.add(dir_key)
                expand_dir(abs_path, Path(root_dir))

        elif abs_path.is_file():
            # 📄 ARCHIVO → solo ese archivo exacto
            add(elem)

        else:
            # No existe → conservar para mostrar warning
            add(elem)

    return result



def build_partial_tree(root_dir, elementos_norm, index_map):
    """
    Árbol visual solo con los elementos solicitados y sus carpetas padre,
    usando los números del índice completo.
    """
    # Expandir todos los paths padres necesarios
    paths_to_show = set()
    for elem in elementos_norm:
        parts = elem.split('/')
        for i in range(1, len(parts) + 1):
            paths_to_show.add('/'.join(parts[:i]))

    # Mapa padre -> hijos (solo los que hay que mostrar)
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
            # Determinar tipo: si existe usamos is_dir(), si no, inferimos por extensión
            if abs_path.exists():
                is_dir = abs_path.is_dir()
            else:
                is_dir = '.' not in name          # sin extensión → carpeta
            icon = '📁' if is_dir else '📄'
            tree_lines.append(f"{prefix}{branch}{num} {icon} {name}")
            if is_dir:
                render(child, next_prefix)

    render('', '')
    return tree_lines


# ====== PROCESAR UNA FUENTE ======

def procesar_fuente(fuente):
    root_dir      = fuente["root"]
    elementos_raw = fuente.get("elementos", [])
    folder_name   = Path(root_dir).name.upper()
    elementos_norm = [e.replace('\\', '/').strip('/') for e in elementos_raw]

    lines = []
    lines.append('▓' * 80)
    lines.append(f"📂 {folder_name}")
    lines.append(f"   Ruta: {root_dir}")
    lines.append('▓' * 80)

    if not os.path.exists(root_dir):
        lines.append(f"❌ Directorio no encontrado: {root_dir}")
        return lines, 0

    if not elementos_norm:
        lines.append("⚠️  Sin elementos definidos para esta fuente.")
        return lines, 0

    # Expandir: archivo -> todos los archivos de su carpeta padre
    #           carpeta -> todos sus archivos recursivamente
    elementos_norm = expand_elementos(root_dir, elementos_norm)

    # Advertir elementos no encontrados (despues de expansion)
    for elem in elementos_norm:
        if not (Path(root_dir) / elem).exists():
            lines.append(f"⚠️  No encontrado: {elem}")

    # Índice completo → numeración real (siempre relativo a root_dir)
    index_map = build_full_index(root_dir, root_dir)

    # Árbol parcial
    lines.append("")
    lines.extend(build_partial_tree(root_dir, elementos_norm, index_map))

    # Código de archivos (en el mismo orden que ELEMENTOS)
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
    print("🚀 Generando esquema de elementos seleccionados (multi-fuente)...")

    if not FUENTES:
        print("⚠️  La lista FUENTES está vacía.")
        return

    all_lines = [
        "📁 FABRICA-AGENTES — ELEMENTOS SELECCIONADOS",
        f"📅 Generado : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"📦 Fuentes  : {len(FUENTES)}",
        "",
    ]

    total_archivos = 0
    for fuente in FUENTES:
        section_lines, count = procesar_fuente(fuente)
        all_lines.extend(section_lines)
        all_lines.append("")
        total_archivos += count
        print(f"   ✔ {Path(fuente['root']).name} → {count} archivo(s)")

    final_text = '\n'.join(all_lines)

    try:
        os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write(final_text)
        print(f"\n✅ Listo: {OUTPUT_FILE}")
        print(f"📊 Total archivos procesados: {total_archivos}")
    except Exception as e:
        print(f"❌ Error al guardar: {str(e)}")


if __name__ == '__main__':
    main()