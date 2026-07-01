from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path


def strip_comments(text: str) -> str:
    return "\n".join(re.sub(r"(?<!\\)%.*$", "", line) for line in text.splitlines())


def main() -> None:
    path = Path(sys.argv[1])
    text = strip_comments(path.read_text(encoding="utf-8"))
    errors: list[str] = []

    depth = 0
    escaped = False
    for index, character in enumerate(text):
        if escaped:
            escaped = False
            continue
        if character == "\\":
            escaped = True
            continue
        if character == "{":
            depth += 1
        elif character == "}":
            depth -= 1
            if depth < 0:
                errors.append(f"Closing brace without opening brace at character {index}")
                depth = 0
    if depth:
        errors.append(f"Unbalanced braces: depth={depth}")

    begins = Counter(re.findall(r"\\begin\{([^}]+)\}", text))
    ends = Counter(re.findall(r"\\end\{([^}]+)\}", text))
    if begins != ends:
        errors.append(f"Environment mismatch. begin={begins - ends}; end={ends - begins}")

    labels = re.findall(r"\\label\{([^}]+)\}", text)
    duplicate_labels = [label for label, count in Counter(labels).items() if count > 1]
    if duplicate_labels:
        errors.append(f"Duplicate labels: {duplicate_labels}")

    references = re.findall(r"\\(?:ref|pageref)\{([^}]+)\}", text)
    missing_labels = sorted(set(references) - set(labels) - {"LastPage"})
    if missing_labels:
        errors.append(f"References without labels: {missing_labels}")

    if "[Nombre del equipo]" not in text:
        errors.append("Expected editable team placeholder is missing")

    print(f"File: {path}")
    print(f"Lines: {len(text.splitlines())}")
    print(f"Labels: {len(labels)}")
    print(f"References: {len(references)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        raise SystemExit(1)
    print("Structural validation: PASS")


if __name__ == "__main__":
    main()
