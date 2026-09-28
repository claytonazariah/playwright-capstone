import json
from pathlib import Path
from typing import Any


def read_json(path: str | Path) -> Any:
    json_path = Path(path)
    with json_path.open(encoding="utf-8") as file:
        return json.load(file)


def write_json(path: str | Path, data: Any) -> None:
    json_path = Path(path)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)