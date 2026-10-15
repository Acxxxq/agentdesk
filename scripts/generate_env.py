"""Generate local Compose credentials without replacing an existing .env."""

import os
import secrets
from pathlib import Path


def private_opener(path: str, flags: int) -> int:
    return os.open(path, flags, 0o600)


def generate(root: Path) -> None:
    template = (root / ".env.example").read_text(encoding="utf-8")
    content = "\n".join(
        line.replace("=CHANGE_ME", "=" + secrets.token_hex(24))
        if line.endswith("=CHANGE_ME") else line
        for line in template.splitlines()
    ) + "\n"
    target = root / ".env"
    # Exclusive creation preserves credentials already associated with data volumes.
    with open(target, "x", encoding="utf-8", opener=private_opener) as stream:
        stream.write(content)
    print("Generated .env with independent random passwords; keep it private.")


if __name__ == "__main__":
    try:
        generate(Path(__file__).resolve().parents[1])
    except FileExistsError:
        raise SystemExit(".env already exists; refusing to overwrite credentials") from None
