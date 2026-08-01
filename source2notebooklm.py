#!/usr/bin/env python3
"""
source2notebooklm - Pack repository source code into LLM / NotebookLM friendly text files.
"""

import argparse
import fnmatch
import os
import sys
from pathlib import Path
from typing import List, Set

# Default directories to ignore across software projects
DEFAULT_IGNORE_DIRS = {
    '.git', 'node_modules', 'venv', '.venv', 'env', '.env', 
    'dist', 'build', 'target', 'out', '__pycache__', '.idea', 
    '.vscode', '.next', '.nuxt', 'bin', 'obj', '.coverage', 
    'coverage', '.pytest_cache', '.mypy_cache', 'graphify-out', 
    '.agents', '.gemini', 'vendor', 'generated', 'generated-sources',
    '.vaadin', '.mvn', 'docs'
}

# Default files to ignore (lockfiles, OS metadata, etc.)
DEFAULT_IGNORE_FILES = {
    'package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 
    'Cargo.lock', 'mix.lock', 'Pipfile.lock', 'skills-lock.json',
    '.DS_Store', 'Thumbs.db'
}

# Default binary or non-text extensions to ignore
DEFAULT_BINARY_EXTENSIONS = {
    '.png', '.jpg', '.jpeg', '.gif', '.ico', '.svg', '.webp',
    '.pdf', '.zip', '.tar', '.gz', '.7z', '.rar', '.exe', '.dll', 
    '.so', '.dylib', '.pyc', '.pyo', '.pyd', '.db', '.sqlite', 
    '.sqlite3', '.woff', '.woff2', '.ttf', '.eot', '.mp3', '.mp4', 
    '.wav', '.avi', '.mov', '.class', '.jar', '.war'
}

# Known backend/frontend extension sets for split mode
BACKEND_EXTENSIONS = {'.java', '.py', '.go', '.rs', '.cpp', '.c', '.h', '.cs', '.php', '.rb', '.properties', '.yml', '.yaml', '.xml', '.sql'}
FRONTEND_EXTENSIONS = {'.ts', '.tsx', '.js', '.jsx', '.css', '.scss', '.html', '.vue', '.svelte', '.json'}
ROOT_FILES_BACKEND = {'pom.xml', 'build.gradle', 'application.properties', 'Cargo.toml', 'go.mod', 'requirements.txt'}
ROOT_FILES_FRONTEND = {'package.json', 'vite.config.ts', 'vite.config.js', 'tsconfig.json', 'next.config.js', 'webpack.config.js'}


def parse_gitignore(root_dir: str) -> List[str]:
    """Reads .gitignore rules from root_dir if it exists."""
    gitignore_path = os.path.join(root_dir, '.gitignore')
    patterns = []
    if os.path.exists(gitignore_path):
        try:
            with open(gitignore_path, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        patterns.append(line)
        except Exception as e:
            print(f"Warning: Could not read .gitignore: {e}", file=sys.stderr)
    return patterns


def is_ignored_by_gitignore(rel_path: str, patterns: List[str]) -> bool:
    """Checks if relative path matches any .gitignore pattern."""
    if not patterns:
        return False
    parts = rel_path.split(os.sep)
    filename = parts[-1]
    
    for pattern in patterns:
        clean_pat = pattern.rstrip('/')
        if fnmatch.fnmatch(rel_path, clean_pat) or fnmatch.fnmatch(filename, clean_pat):
            return True
        for part in parts:
            if fnmatch.fnmatch(part, clean_pat):
                return True
    return False


def get_language_from_ext(ext: str) -> str:
    """Maps file extension to markdown codeblock language tag."""
    mapping = {
        '.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.tsx': 'tsx',
        '.jsx': 'jsx', '.html': 'html', '.css': 'css', '.scss': 'scss',
        '.java': 'java', '.cpp': 'cpp', '.c': 'c', '.h': 'cpp',
        '.cs': 'csharp', '.go': 'go', '.rs': 'rust', '.php': 'php',
        '.rb': 'ruby', '.json': 'json', '.yaml': 'yaml', '.yml': 'yaml',
        '.xml': 'xml', '.sql': 'sql', '.md': 'markdown', '.sh': 'bash'
    }
    return mapping.get(ext.lower(), '')


def categorize_file(rel_path: str) -> str:
    """Categorizes file into 'backend' or 'frontend' for split mode."""
    parts = rel_path.split(os.sep)
    filename = parts[-1].lower()
    
    if filename in ROOT_FILES_BACKEND:
        return 'backend'
    if filename in ROOT_FILES_FRONTEND:
        return 'frontend'
    
    if 'frontend' in parts:
        return 'frontend'
    if 'backend' in parts or 'server' in parts:
        return 'backend'
        
    _, ext = os.path.splitext(filename)
    if ext in BACKEND_EXTENSIONS:
        return 'backend'
    if ext in FRONTEND_EXTENSIONS:
        return 'frontend'
        
    return 'other'


def format_file_content(rel_path: str, content: str, fmt: str) -> str:
    """Formats file content block depending on specified format ('txt' or 'md')."""
    if fmt == 'md':
        _, ext = os.path.splitext(rel_path)
        lang = get_language_from_ext(ext)
        return f"## File: `{rel_path}`\n```{lang}\n{content}\n```\n\n"
    else:
        header = f"// --- ARCHIVO: {rel_path} ---"
        return f"{header}\n{content}\n\n"


def main():
    parser = argparse.ArgumentParser(
        description="Pack codebase into clean text/markdown files for NotebookLM and LLM context limits."
    )
    parser.add_argument(
        'path', nargs='?', default='.',
        help="Root directory of the project to scan (default: current directory)."
    )
    parser.add_argument(
        '-o', '--output', default='notebooklm_codebase.txt',
        help="Output file name/path (default: notebooklm_codebase.txt)."
    )
    parser.add_argument(
        '--format', choices=['txt', 'md'], default='txt',
        help="Output format style: 'txt' (comments header) or 'md' (Markdown codeblocks). Default: txt."
    )
    parser.add_argument(
        '--split-frontend-backend', action='store_true',
        help="Separate output into backend and frontend text files."
    )
    parser.add_argument(
        '--include-ext', help="Comma-separated file extensions to include (e.g., .py,.ts,.java)."
    )
    parser.add_argument(
        '--exclude-ext', help="Comma-separated file extensions to exclude."
    )
    parser.add_argument(
        '--ignore-dirs', help="Comma-separated additional directory names to ignore."
    )
    parser.add_argument(
        '--ignore-files', help="Comma-separated additional file names to ignore."
    )
    parser.add_argument(
        '--max-size-kb', type=int, default=1000,
        help="Maximum file size in KB to process (default: 1000 KB)."
    )
    parser.add_argument(
        '--no-gitignore', action='store_true',
        help="Do not read .gitignore rules."
    )

    args = parser.parse_args()

    project_dir = os.path.abspath(args.path)
    if not os.path.isdir(project_dir):
        print(f"Error: Directory '{project_dir}' does not exist.", file=sys.stderr)
        sys.exit(1)

    # Build ignore sets
    ignore_dirs = set(DEFAULT_IGNORE_DIRS)
    if args.ignore_dirs:
        ignore_dirs.update(d.strip() for d in args.ignore_dirs.split(','))

    ignore_files = set(DEFAULT_IGNORE_FILES)
    if args.ignore_files:
        ignore_files.update(f.strip() for f in args.ignore_files.split(','))

    include_ext = set(e.strip().lower() for e in args.include_ext.split(',')) if args.include_ext else None
    exclude_ext = set(e.strip().lower() for e in args.exclude_ext.split(',')) if args.exclude_ext else set()
    exclude_ext.update(DEFAULT_BINARY_EXTENSIONS)

    gitignore_patterns = [] if args.no_gitignore else parse_gitignore(project_dir)

    print(f"Scanning directory: {project_dir}")
    if gitignore_patterns:
        print(f"Loaded {len(gitignore_patterns)} rules from .gitignore")

    files_processed = 0
    total_lines = 0
    total_chars = 0

    if args.split_frontend_backend:
        backend_content = []
        frontend_content = []
        other_content = []

        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [
                d for d in dirs 
                if d not in ignore_dirs and not is_ignored_by_gitignore(
                    os.path.relpath(os.path.join(root, d), project_dir), gitignore_patterns
                )
            ]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)
                
                if file in ignore_files or is_ignored_by_gitignore(rel_path, gitignore_patterns):
                    continue

                _, ext = os.path.splitext(file)
                ext = ext.lower()

                if include_ext and ext not in include_ext:
                    continue
                if ext in exclude_ext:
                    continue

                try:
                    if os.path.getsize(full_path) > args.max_size_kb * 1024:
                        print(f"Skipping large file ({os.path.getsize(full_path)//1024} KB): {rel_path}")
                        continue
                    
                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    block = format_file_content(rel_path, content, args.format)
                    cat = categorize_file(rel_path)

                    if cat == 'backend':
                        backend_content.append(block)
                    elif cat == 'frontend':
                        frontend_content.append(block)
                    else:
                        other_content.append(block)

                    files_processed += 1
                    total_lines += content.count('\n') + 1
                    total_chars += len(block)
                    print(f"[{cat.upper()}] Added: {rel_path}")

                except Exception as e:
                    print(f"Error reading {rel_path}: {e}", file=sys.stderr)

        base_out, out_ext = os.path.splitext(args.output)
        if not out_ext:
            out_ext = '.txt' if args.format == 'txt' else '.md'
            
        backend_file = f"{base_out}_backend{out_ext}"
        frontend_file = f"{base_out}_frontend{out_ext}"

        with open(backend_file, 'w', encoding='utf-8') as f:
            f.writelines(backend_content)
        print(f"\nWritten Backend code to: {backend_file}")

        with open(frontend_file, 'w', encoding='utf-8') as f:
            f.writelines(frontend_content)
        print(f"Written Frontend code to: {frontend_file}")

        if other_content:
            other_file = f"{base_out}_other{out_ext}"
            with open(other_file, 'w', encoding='utf-8') as f:
                f.writelines(other_content)
            print(f"Written Other code to: {other_file}")

    else:
        all_content = []

        for root, dirs, files in os.walk(project_dir):
            dirs[:] = [
                d for d in dirs 
                if d not in ignore_dirs and not is_ignored_by_gitignore(
                    os.path.relpath(os.path.join(root, d), project_dir), gitignore_patterns
                )
            ]
            
            for file in files:
                full_path = os.path.join(root, file)
                rel_path = os.path.relpath(full_path, project_dir)

                if file in ignore_files or is_ignored_by_gitignore(rel_path, gitignore_patterns):
                    continue

                _, ext = os.path.splitext(file)
                ext = ext.lower()

                if include_ext and ext not in include_ext:
                    continue
                if ext in exclude_ext:
                    continue

                try:
                    if os.path.getsize(full_path) > args.max_size_kb * 1024:
                        print(f"Skipping large file ({os.path.getsize(full_path)//1024} KB): {rel_path}")
                        continue

                    with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    block = format_file_content(rel_path, content, args.format)
                    all_content.append(block)

                    files_processed += 1
                    total_lines += content.count('\n') + 1
                    total_chars += len(block)
                    print(f"Added: {rel_path}")

                except Exception as e:
                    print(f"Error reading {rel_path}: {e}", file=sys.stderr)

        out_path = args.output
        with open(out_path, 'w', encoding='utf-8') as f:
            f.writelines(all_content)
        print(f"\nWritten codebase summary to: {out_path}")

    # Final Statistics Summary
    size_mb = total_chars / (1024 * 1024)
    est_tokens = total_chars // 4
    print("\n" + "=" * 40)
    print(" SUMMARY STATISTICS")
    print("=" * 40)
    print(f"Total Files Processed: {files_processed}")
    print(f"Total Lines of Code:   {total_lines:,}")
    print(f"Total Output Size:     {size_mb:.2f} MB ({total_chars:,} characters)")
    print(f"Estimated Tokens:      ~{est_tokens:,} tokens")
    print("=" * 40)
    print("Done! Ready to upload to NotebookLM.")


if __name__ == "__main__":
    main()
