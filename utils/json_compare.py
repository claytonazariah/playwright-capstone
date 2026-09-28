from typing import Any


def json_mismatch_paths(actual: Any, expected: Any, path: str = "root") -> list[str]:
    if isinstance(actual, dict) and isinstance(expected, dict):
        mismatches = []
        keys = actual.keys() | expected.keys()
        for key in sorted(keys):
            child_path = f"{path}.{key}"
            if key not in actual or key not in expected:
                mismatches.append(child_path)
            else:
                mismatches.extend(json_mismatch_paths(actual[key], expected[key], child_path))
        return mismatches

    if isinstance(actual, list) and isinstance(expected, list):
        mismatches = []
        for index in range(max(len(actual), len(expected))):
            child_path = f"{path}[{index}]"
            if index >= len(actual) or index >= len(expected):
                mismatches.append(child_path)
            else:
                mismatches.extend(json_mismatch_paths(actual[index], expected[index], child_path))
        return mismatches

    if type(actual) is not type(expected) or actual != expected:
        return [path]
    return []


def assert_json_deep_equal(actual: Any, expected: Any) -> None:
    mismatches = json_mismatch_paths(actual, expected)
    if mismatches:
        paths = ", ".join(mismatches)
        raise AssertionError(f"JSON values differ at: {paths}")