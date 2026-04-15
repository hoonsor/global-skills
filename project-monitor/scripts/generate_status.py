#!/usr/bin/env python3
"""
generate_status.py — 為個別專案產生或更新 PROJECT_STATUS.md

使用方式：
  python generate_status.py --project "D:\01-Project\01-Screen Automate"
  python generate_status.py --project "D:\01-Project\06-全能生活網頁" --force
"""

import os
import sys
import json
import re
import subprocess
import argparse
from datetime import datetime
from pathlib import Path

# ─── Windows 終端 UTF-8 修正 ───
if sys.platform == "win32":
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# 模板路徑
TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")
TEMPLATE_PATH = os.path.join(TEMPLATE_DIR, "PROJECT_STATUS_TEMPLATE.md")


def get_git_remote(project_path: str) -> str | None:
    """從 git config 取得遠端倉庫 URL。"""
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


def get_version(project_path: str) -> str:
    """從 package.json / pyproject.toml 提取版本號。"""
    pkg_json = os.path.join(project_path, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                ver = data.get("version")
                if ver:
                    return ver
        except (json.JSONDecodeError, OSError):
            pass

    pyproject = os.path.join(project_path, "pyproject.toml")
    if os.path.exists(pyproject):
        try:
            with open(pyproject, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r'version\s*=\s*"([^"]+)"', content)
                if match:
                    return match.group(1)
        except OSError:
            pass

    return "0.1.0"


def get_description(project_path: str) -> str:
    """從 README.md 提取描述。"""
    readme = os.path.join(project_path, "README.md")
    if os.path.exists(readme):
        try:
            with open(readme, "r", encoding="utf-8") as f:
                lines = f.readlines()
                desc_lines = []
                found_title = False
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("#") and not found_title:
                        found_title = True
                        continue
                    if found_title and stripped:
                        if stripped.startswith("#"):
                            break
                        desc_lines.append(stripped)
                    elif found_title and not stripped and desc_lines:
                        break
                if desc_lines:
                    return " ".join(desc_lines)
        except OSError:
            pass
    return "請在此填寫專案功能概述。"


def get_project_name(project_path: str) -> str:
    """取得專案名稱。"""
    # 嘗試從 README.md 的標題取得
    readme = os.path.join(project_path, "README.md")
    if os.path.exists(readme):
        try:
            with open(readme, "r", encoding="utf-8") as f:
                first_line = f.readline().strip()
                if first_line.startswith("#"):
                    return first_line.lstrip("#").strip()
        except OSError:
            pass

    # 嘗試從 package.json 取得
    pkg_json = os.path.join(project_path, "package.json")
    if os.path.exists(pkg_json):
        try:
            with open(pkg_json, "r", encoding="utf-8") as f:
                data = json.load(f)
                name = data.get("name")
                if name:
                    return name
        except (json.JSONDecodeError, OSError):
            pass

    # 使用資料夾名稱
    return os.path.basename(project_path)


def get_git_log_for_changelog(project_path: str, max_entries: int = 20) -> list[dict]:
    """從 git log 產生初始 changelog。"""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{max_entries}", "--pretty=format:%ai|%s"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            entries = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 1)
                    date_str = parts[0].strip()[:10]  # YYYY-MM-DD
                    message = parts[1].strip() if len(parts) > 1 else ""

                    # 嘗試解析 conventional commit 類型
                    type_match = re.match(
                        r"(feat|fix|refactor|docs|style|perf|test|chore)(\(.+?\))?:\s*(.+)",
                        message,
                    )
                    if type_match:
                        change_type = type_match.group(1)
                        desc = type_match.group(3)
                    else:
                        change_type = "chore"
                        desc = message

                    entries.append(
                        {"date": date_str, "type": change_type, "description": desc}
                    )
            return entries
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return []


def generate_status(project_path: str, force: bool = False) -> str:
    """為專案產生 PROJECT_STATUS.md。"""
    status_path = os.path.join(project_path, "PROJECT_STATUS.md")

    if os.path.exists(status_path) and not force:
        print(f"⚠️  PROJECT_STATUS.md 已存在：{status_path}")
        print(f"   使用 --force 強制重新產生")
        return status_path

    # 收集資料
    project_name = get_project_name(project_path)
    version = get_version(project_path)
    github_url = get_git_remote(project_path) or "尚未設定"
    description = get_description(project_path)
    today = datetime.now().strftime("%Y-%m-%d")

    # 讀取模板
    try:
        with open(TEMPLATE_PATH, "r", encoding="utf-8") as f:
            template = f.read()
    except OSError:
        print(f"❌ 無法讀取模板：{TEMPLATE_PATH}")
        sys.exit(1)

    # 填充模板
    content = template.replace("{project_name}", project_name)
    content = content.replace("{version}", version)
    content = content.replace("{last_updated}", today)
    content = content.replace("{github_url}", github_url)
    content = content.replace("{description}", description)
    content = content.replace("{main_task_placeholder}", "待定義主要任務")
    content = content.replace("{sub_task_placeholder}", "待定義次要任務")
    content = content.replace("{current_direction}", "請在此描述目前的專案發展方向。")

    # 如果有 git log，豐富 changelog 表格
    has_git = os.path.isdir(os.path.join(project_path, ".git"))
    if has_git:
        git_entries = get_git_log_for_changelog(project_path, max_entries=10)
        if git_entries:
            changelog_rows = []
            for entry in git_entries:
                changelog_rows.append(
                    f"| v{version} | {entry['date']} | {entry['type']} | {entry['description']} |"
                )
            # 替換模板中的初始 changelog 行
            initial_row = f"| v{version} | {today} | feat | 初始版本建立 |"
            content = content.replace(
                initial_row, "\n".join(changelog_rows[:5])  # 最多放 5 條
            )

    # 寫入檔案
    with open(status_path, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"✅ 已產生：{status_path}")
    return status_path


def main():
    parser = argparse.ArgumentParser(
        description="為個別專案產生 PROJECT_STATUS.md"
    )
    parser.add_argument(
        "--project",
        required=True,
        help="專案資料夾的完整路徑",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="強制覆蓋已存在的 PROJECT_STATUS.md",
    )
    args = parser.parse_args()

    if not os.path.isdir(args.project):
        print(f"❌ 錯誤：目錄不存在 — {args.project}")
        sys.exit(1)

    print(f"📝 產生 PROJECT_STATUS.md")
    print(f"📁 專案：{args.project}")
    print(f"{'='*50}")

    generate_status(args.project, args.force)


if __name__ == "__main__":
    main()
