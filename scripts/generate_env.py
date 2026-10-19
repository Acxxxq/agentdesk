"""从模板创建本地开发环境文件；真实 API 密钥由开发者自行填写。"""

from pathlib import Path


def generate(root: Path) -> None:
    """复制 `.env.example` 为 `.env`，已有配置时拒绝覆盖。

    参数：
        root：项目根目录，必须包含 `.env.example`。

    返回：
        None：创建文件并提示后续配置步骤；目标已存在时抛出 FileExistsError。
    """
    source = root / ".env.example"
    target = root / ".env"
    with target.open("x", encoding="utf-8", newline="\n") as stream:
        stream.write(source.read_text(encoding="utf-8"))
    print("已创建 .env。请填写 ANTHROPIC_API_KEY；该文件已被 Git 忽略。")


if __name__ == "__main__":
    try:
        generate(Path(__file__).resolve().parents[1])
    except FileExistsError:
        raise SystemExit(".env 已存在，为保护本地密钥拒绝覆盖。") from None
