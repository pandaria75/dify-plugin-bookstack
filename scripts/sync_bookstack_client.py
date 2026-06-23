from __future__ import annotations

import argparse
import ast
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE_PATH = ROOT / "bookstack_client.py"
TARGET_PATH = ROOT / "bookstack_datasource" / "bookstack_client.py"

ERROR_CLASSES = [
    "BookStackError",
    "InvalidCredentialsError",
    "PermissionDeniedError",
    "BookNotFoundError",
    "ChapterNotFoundError",
    "PageNotFoundError",
    "ServiceUnavailableError",
    "InvalidResponseError",
]
HELPER_FUNCTIONS = [
    "_invalid_credentials",
    "_service_unavailable",
    "_invalid_response",
]
CLIENT_METHODS = [
    "from_credentials",
    "_require_credential",
    "_parse_timeout",
    "_parse_verify_ssl",
    "_api_url",
    "_session",
    "_request",
    "validate_credentials",
    "list_pages",
    "list_chapters",
    "get_page",
]


def _node_text(source: str, node: ast.AST) -> str:
    segment = ast.get_source_segment(source, node)
    if segment is None:
        raise ValueError(f"Unable to extract source for node: {type(node).__name__}")
    return segment.rstrip()


def _line_text(lines: list[str], start_line: int, end_line: int) -> str:
    return "\n".join(lines[start_line - 1 : end_line]).rstrip()


def _statement_text(lines: list[str], node: ast.AST) -> str:
    start_line = getattr(node, "lineno")
    decorators = getattr(node, "decorator_list", [])
    if decorators:
        start_line = min(start_line, *(decorator.lineno for decorator in decorators))
    return _line_text(lines, start_line, getattr(node, "end_lineno"))


def _build_client_class(source: str, class_node: ast.ClassDef) -> str:
    lines = source.splitlines()
    class_parts: list[str] = []

    header_start = min([decorator.lineno for decorator in class_node.decorator_list], default=class_node.lineno)
    header_end = class_node.body[0].lineno - 1
    class_parts.append(_line_text(lines, header_start, header_end))

    for node in class_node.body:
        if isinstance(node, ast.AnnAssign):
            class_parts.append(_line_text(lines, node.lineno, node.end_lineno))
            continue

        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name in CLIENT_METHODS:
            class_parts.append(_statement_text(lines, node))

    return "\n\n".join(class_parts)


def render_datasource_client() -> str:
    source = SOURCE_PATH.read_text(encoding="utf-8")
    module = ast.parse(source)

    imports: list[str] = []
    top_level_nodes: dict[str, ast.AST] = {}
    client_class: ast.ClassDef | None = None

    for node in module.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            imports.append(_node_text(source, node))
        elif isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            top_level_nodes[node.name] = node
            if isinstance(node, ast.ClassDef) and node.name == "BookStackClient":
                client_class = node

    if client_class is None:
        raise ValueError("Canonical BookStackClient class not found")

    sections = ["\n".join(imports)]
    sections.extend(_node_text(source, top_level_nodes[name]) for name in ERROR_CLASSES)
    sections.extend(_node_text(source, top_level_nodes[name]) for name in HELPER_FUNCTIONS)
    sections.append(_build_client_class(source, client_class))

    return "\n\n\n".join(sections) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync generated datasource BookStack client")
    parser.add_argument("--check", action="store_true", help="Fail if generated output differs")
    args = parser.parse_args()

    rendered = render_datasource_client()
    current = TARGET_PATH.read_text(encoding="utf-8") if TARGET_PATH.exists() else None

    if args.check:
        if current != rendered:
            print(f"Drift detected: {TARGET_PATH}", file=sys.stderr)
            return 1
        print(f"Up to date: {TARGET_PATH}")
        return 0

    TARGET_PATH.write_text(rendered, encoding="utf-8")
    print(f"Updated: {TARGET_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
