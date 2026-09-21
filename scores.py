import json
from pathlib import Path

PATH = Path("highscore.json")

def load_best() -> int:
    if not PATH.is_file():
        return 0
    data = json.loads(PATH.read_text())
    return int(data.get("best", 0))

def save_best(score: int) -> None:
    PATH.write_text(json.dumps({"best": score}))
