import os
import zipfile
import argparse
from typing import Iterable


def create_zip(root: str, zip_name: str, exclude_dirs: Iterable[str], allowed_exts: Iterable[str]) -> int:
    exclude_set = set(exclude_dirs)
    allowed = set(e.lower() for e in allowed_exts) if allowed_exts else set()
    with zipfile.ZipFile(zip_name, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
        for dirpath, dirnames, filenames in os.walk(root):
            rel_dir = os.path.relpath(dirpath, root)
            parts = [] if rel_dir == '.' else rel_dir.split(os.sep)
            if any(p in exclude_set for p in parts):
                continue
            for fname in filenames:
                # skip the zip script itself
                if fname == os.path.basename(__file__):
                    continue
                full = os.path.join(dirpath, fname)
                # skip the target zip if it's in the tree
                if os.path.abspath(full) == os.path.abspath(zip_name):
                    continue
                _, ext = os.path.splitext(fname)
                if not allowed or ext.lower() in allowed:
                    arcname = os.path.relpath(full, root)
                    zf.write(full, arcname)
    return os.path.getsize(zip_name)


def parse_list(s: str) -> list:
    return [p.strip() for p in s.split(',') if p.strip()] if s else []


def main():
    parser = argparse.ArgumentParser(description='Create a trimmed ZIP of the workspace')
    parser.add_argument('--output', '-o', default='sprint_a_task.zip', help='Output zip file name')
    parser.add_argument('--exclude-dirs', default='myenv,.venv,venv,data,logs,reports,__pycache__,.git,node_modules',
                        help='Comma-separated directories to exclude')
    parser.add_argument('--exts', default='.py,.md,.txt,.json,.yml,.yaml,.ini,.cfg,.csv',
                        help='Comma-separated allowed file extensions (include the dot). Empty = include all')
    parser.add_argument('--max-size-mb', type=int, default=50, help='Max allowed size in MB for quick check')
    args = parser.parse_args()

    root = os.getcwd()
    zip_name = os.path.abspath(args.output)
    exclude_dirs = parse_list(args.exclude_dirs)
    allowed_exts = parse_list(args.exts)

    size = create_zip(root, zip_name, exclude_dirs, allowed_exts)
    print(f'Created {zip_name} ({size} bytes)')
    if size > args.max_size_mb * 1024 * 1024:
        print(f'ZIP exceeds {args.max_size_mb}MB. Consider excluding more files or directories.')
    else:
        print(f'ZIP is under {args.max_size_mb}MB.')


if __name__ == '__main__':
    main()
