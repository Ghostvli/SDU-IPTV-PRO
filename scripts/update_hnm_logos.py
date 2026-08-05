#!/usr/bin/env python3
"""
根据 logo/河南/ 目录下的新 logo 文件，更新 external/HNM-Unicast.m3u 和
external/HNM-Unicast-lite.m3u 中的 tvg-logo 字段。

规则：
- 频道名能精确匹配到 logo/河南/<频道名>.png 时，使用最具体的 logo。
- 否则按所属市/县匹配到 logo/河南/<城市名>.png。
- 对于河南省级频道，使用 河南/河南<频道名>.png。
- 完全没有匹配且无 logo 的频道，保持原样不强行添加（避免引入错误 logo）。
"""
import re
from pathlib import Path

BASE_DIR = Path(r"d:\00trae\SDU-IPTV-PRO")
LOGO_DIR = BASE_DIR / "logo" / "河南"
LOG_PROXY = "https://gh-proxy.org/https://raw.githubusercontent.com/sggc/SDU-IPTV-PRO/main/logo/河南"

TARGET_FILES = [
    BASE_DIR / "external" / "HNM-Unicast.m3u",
    BASE_DIR / "external" / "HNM-Unicast-lite.m3u",
    BASE_DIR / "external" / "HNT-Unicast-full.m3u",
    BASE_DIR / "external" / "HNT-Unicast.m3u",
    BASE_DIR / "external" / "HNU-Multicast.m3u",
]


def load_logo_index() -> set:
    """读取 logo/河南 目录下所有 .png 文件名（不含扩展名）。"""
    return {p.stem for p in LOGO_DIR.glob("*.png")}


def find_logo_for_channel(channel_name: str, logo_index: set) -> str | None:
    """
    根据频道名查找最合适的 logo 文件名（不含扩展名）。
    优先级：精确匹配 → 前缀匹配（按长度从长到短，取最长匹配）
    """
    if channel_name in logo_index:
        return channel_name

    # 收集所有可能的前缀匹配（频道名以该 logo 名开头）
    candidates = [
        logo_name for logo_name in logo_index
        if not logo_name.startswith("河南")
        and len(logo_name) >= 2
        and channel_name.startswith(logo_name)
        and len(channel_name) > len(logo_name)
    ]

    if not candidates:
        return None

    # 取最长前缀匹配
    return max(candidates, key=len)


def update_m3u_file(file_path: Path, logo_index: set) -> tuple[int, int, int]:
    """
    更新单个 m3u 文件。
    返回 (修改数量, 新增logo数量, 总处理数)。
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    modified_count = 0
    added_logo_count = 0
    processed_count = 0

    def process_extinf(match: re.Match) -> str:
        nonlocal modified_count, added_logo_count, processed_count
        extinf_attrs = match.group(1)
        channel_name = match.group(2).strip()

        processed_count += 1
        existing_logo_match = re.search(r'tvg-logo="([^"]*)"', extinf_attrs)
        existing_logo = existing_logo_match.group(1) if existing_logo_match else None

        logo_stem = find_logo_for_channel(channel_name, logo_index)
        if logo_stem is None:
            return match.group(0)

        new_logo_url = f"{LOG_PROXY}/{logo_stem}.png"

        if existing_logo == new_logo_url:
            return match.group(0)

        if existing_logo is None:
            new_attrs = extinf_attrs + f' tvg-logo="{new_logo_url}"'
            added_logo_count += 1
        else:
            new_attrs = re.sub(r'tvg-logo="[^"]*"', f'tvg-logo="{new_logo_url}"', extinf_attrs)
            modified_count += 1

        return f"#EXTINF:-1 {new_attrs},{channel_name}"

    pattern = r'#EXTINF:-1 (.*?),(.*?)(?=\n)'
    new_content = re.sub(pattern, process_extinf, content)

    if new_content != content:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)

    return modified_count, added_logo_count, processed_count


def main():
    logo_index = load_logo_index()
    print(f"已加载 {len(logo_index)} 个 logo 文件")
    print()

    for file_path in TARGET_FILES:
        if not file_path.exists():
            print(f"[跳过] 文件不存在: {file_path}")
            continue
        print(f"处理: {file_path.relative_to(BASE_DIR)}")
        modified, added, total = update_m3u_file(file_path, logo_index)
        print(f"  - 处理频道总数: {total}")
        print(f"  - 修改已存在 logo: {modified}")
        print(f"  - 新增 logo: {added}")
        print()


if __name__ == "__main__":
    main()
