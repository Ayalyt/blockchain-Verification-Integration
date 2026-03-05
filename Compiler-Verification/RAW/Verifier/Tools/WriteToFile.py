from pathlib import Path


def save_string_to_file(content: str, path: str):
    try:
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)  # 若目录不存在则创建
        p.write_text(str(content), encoding="utf-8")
        print(f"[OK] 文件已保存到: {p.resolve()}")
    except Exception as e:
        print(f"[ERROR] 写入文件失败: {e}")
