import re


def remove_empty_strings(strings: list[str]) -> list[str]:
    return [s for s in strings if s is not None and s.strip()]


def search_by_pattern(src_string: str, pattern: str, group_num: int) -> str | None:
    p = re.compile(pattern)
    matched = p.search(src_string)
    return matched.group(group_num) if matched else None
