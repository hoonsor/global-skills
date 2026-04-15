#!/usr/bin/env python3
"""
scan_projects.py — 批次掃描 D:\01-Project\ 下所有專案，產出統一 JSON
供監控網站前端介接使用。

使用方式：
  python scan_projects.py
  python scan_projects.py --base-dir "D:\01-Project"
  python scan_projects.py --output "D:\output\projects.json"
"""

import os
import sys
import json
import re
import subprocess
import argparse
import time
import urllib.request
import urllib.parse
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

# ─── 預設設定 ───────────────────────────────────────────────────
DEFAULT_BASE_DIR = r"D:\01-Project"
DEFAULT_OUTPUT_DIR = os.path.join(DEFAULT_BASE_DIR, "08-監控AI各專案進度之網站", "data")


# ─── 翻譯工具 ───────────────────────────────────────────────────

def is_mostly_chinese(text: str) -> bool:
    """判斷文字是否已經主要為中文。"""
    if not text:
        return False
    cjk_count = 0
    ascii_count = 0
    for ch in text:
        if '\u4e00' <= ch <= '\u9fff' or '\u3400' <= ch <= '\u4dbf':
            cjk_count += 1
        elif ch.isascii() and ch.isalpha():
            ascii_count += 1
    total = cjk_count + ascii_count
    if total == 0:
        return True
    return (cjk_count / total) > 0.3


def translate_to_zh_tw(text: str) -> str:
    """使用免費的 Google Translate API 進行英翻繁體中文。
    若文字已經主要為中文則跳過翻譯。"""
    if not text or not text.strip() or len(text) < 5:
        return text
    if is_mostly_chinese(text):
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=zh-TW&dt=t&q=" + urllib.parse.quote(text[:2000])
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=8) as response:
            result = json.loads(response.read().decode('utf-8'))
            val = "".join([sentence[0] for sentence in result[0] if sentence[0]])
            time.sleep(0.15)  # 避免請求過快被鎖
            return val
    except Exception:
        return text


# ─── Git 工具 ───────────────────────────────────────────────────

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


def get_git_log(project_path: str, max_entries: int = 50) -> list[dict]:
    """取得 git commit 紀錄。"""
    try:
        result = subprocess.run(
            ["git", "log", f"-n{max_entries}", "--pretty=format:%H|%ai|%s"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 2)
                    commits.append(
                        {
                            "hash": parts[0],
                            "date": parts[1].strip(),
                            "message": parts[2].strip() if len(parts) > 2 else "",
                        }
                    )
            return commits
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return []


def get_last_commit_date(project_path: str) -> str | None:
    """取得最後一次 commit 的時間。"""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%aI"],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass
    return None


# ─── 版本與描述提取 ───────────────────────────────────────────────

def get_version(project_path: str) -> str:
    """從 package.json / pyproject.toml / PROJECT_STATUS.md 提取版本號。"""
    # 1. package.json
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

    # 2. pyproject.toml (簡易解析，不引入 toml 庫)
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

    # 3. PROJECT_STATUS.md
    status_md = os.path.join(project_path, "PROJECT_STATUS.md")
    if os.path.exists(status_md):
        try:
            with open(status_md, "r", encoding="utf-8") as f:
                content = f.read()
                match = re.search(r"版本號[：:]\s*`?v?(\d+\.\d+\.\d+)", content)
                if match:
                    return match.group(1)
        except OSError:
            pass

    return "0.0.0"


def get_description(project_path: str) -> str | None:
    """從 README.md 提取專案描述（保留換行格式），優先尋找「簡介」區塊。
    提取後會自動將英文內容翻譯為繁體中文。"""
    readme = os.path.join(project_path, "README.md")
    if os.path.exists(readme):
        try:
            with open(readme, "r", encoding="utf-8") as f:
                lines = f.readlines()
                
                desc_lines = []
                started = False
                in_overview_section = False
                
                for line in lines:
                    stripped = line.strip()
                    
                    # 偵測大標題開始
                    if stripped.startswith("# ") and not started:
                        started = True
                        continue
                        
                    if not started:
                        continue
                        
                    # 偵測是否進入明顯的簡介區塊
                    if stripped.startswith("## ") and ("簡介" in stripped or "概述" in stripped or "Overview" in stripped.lower()):
                        desc_lines = []  # 清空之前的（可能是簡短描述），重新開始收集
                        in_overview_section = True
                        continue
                        
                    # 遇到其他副標題時停止
                    if stripped.startswith("## ") and not in_overview_section:
                        break
                    elif stripped.startswith("## ") and in_overview_section:
                        break
                        
                    desc_lines.append(line.rstrip())
                    
                # 去除開頭與結尾的空行
                while desc_lines and not desc_lines[0].strip():
                    desc_lines.pop(0)
                while desc_lines and not desc_lines[-1].strip():
                    desc_lines.pop()
                    
                result = "\n".join(desc_lines)
                
                if len(result) > 1000:
                    result = result[:1000] + "...\n(詳情請見 README.md)"
                
                # ★ 翻譯為中文
                if result:
                    print("    📝 翻譯描述...", end=" ")
                    result = translate_to_zh_tw(result)
                    print("OK")

                return result if result else None
        except OSError:
            pass
    return None


def get_project_name(project_path: str, folder_name: str) -> str:
    """取得專案名稱。
    
    策略：
    1. 優先使用資料夾名稱（因為是使用者自定義、最具辨識度的名稱）
    2. 若資料夾名只有編號前綴（如 '01-'），才嘗試從 PROJECT_STATUS.md 或 README.md 補充
    """
    # ★ 直接使用資料夾名稱做為主要名稱
    return folder_name


# ─── 版本歷程解析 ───────────────────────────────────────────────

def parse_status_file(project_path: str) -> dict:
    """解析 PROJECT_STATUS.md，提取 changelog、tasks、revision_history。
    changelog 中的描述若為英文會自動翻譯為中文。"""
    result = {
        "changelog": [],
        "tasks": {"main": [], "sub": [], "deprecated": []},
        "revision_history": [],
    }

    status_md = os.path.join(project_path, "PROJECT_STATUS.md")
    if not os.path.exists(status_md):
        return result

    try:
        with open(status_md, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return result

    # ─── 解析任務核取方塊 ───
    task_pattern = re.compile(r"- \[([ x/])\] (.+)")
    current_section = None

    for line in content.split("\n"):
        line_stripped = line.strip()

        # 偵測任務區塊標題
        if re.search(r"###?\s*主要任務", line_stripped):
            current_section = "main"
            continue
        elif re.search(r"###?\s*次要任務", line_stripped):
            current_section = "sub"
            continue
        elif line_stripped.startswith("#"):
            # 遇到其他標題就重設
            if current_section in ("main", "sub"):
                current_section = None

        match = task_pattern.match(line_stripped)
        if match and current_section in ("main", "sub"):
            status_char = match.group(1)
            title = match.group(2)
            result["tasks"][current_section].append(
                {
                    "title": title,
                    "completed": status_char == "x",
                    "in_progress": status_char == "/",
                }
            )

    # ─── 解析棄用項目（刪除線） ───
    deprecated_pattern = re.compile(r"~~(.+?)~~")
    # 只解析在「歷次修訂紀錄」或 callout 區塊中的刪除線
    in_revision_section = False
    for line in content.split("\n"):
        if re.search(r"###?\s*歷(次|史)修訂", line):
            in_revision_section = True
        elif line.startswith("# ") or line.startswith("## "):
            if in_revision_section and "修訂" not in line:
                in_revision_section = False

        if in_revision_section:
            for dep_match in deprecated_pattern.finditer(line):
                result["tasks"]["deprecated"].append(
                    {"title": dep_match.group(1), "deprecated": True}
                )

    # ─── 解析版本歷程表格 ───
    table_pattern = re.compile(
        r"\|\s*v?(\d+\.\d+\.\d+)\s*\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(\w+)\s*\|\s*(.+?)\s*\|"
    )
    for match in table_pattern.finditer(content):
        desc = match.group(4).strip()
        # ★ 翻譯版本歷程描述
        desc = translate_to_zh_tw(desc)
        result["changelog"].append(
            {
                "version": match.group(1),
                "date": match.group(2),
                "type": match.group(3),
                "description": desc,
            }
        )

    # ─── 解析修訂紀錄 callout ───
    callout_pattern = re.compile(
        r">\s*\*\*已棄用方向\s*\((\d{4}-\d{2}-\d{2})\)\*\*\s*\n"
        r">\s*~~(.+?)~~\s*\n"
        r"(?:>\s*\*\*棄用原因[：:]\*\*\s*(.+))?"
    )
    for match in callout_pattern.finditer(content):
        result["revision_history"].append(
            {
                "date": match.group(1),
                "old_direction": match.group(2),
                "reason": match.group(3).strip() if match.group(3) else "",
            }
        )

    return result


# ─── 技術棧偵測 ───────────────────────────────────────────────

def detect_tech_stack(project_path: str) -> list[str]:
    """偵測專案使用的技術棧。"""
    techs = []

    if os.path.exists(os.path.join(project_path, "package.json")):
        try:
            with open(
                os.path.join(project_path, "package.json"), "r", encoding="utf-8"
            ) as f:
                pkg = json.load(f)
                deps = {
                    **pkg.get("dependencies", {}),
                    **pkg.get("devDependencies", {}),
                }
                if "next" in deps:
                    techs.append("Next.js")
                if "react" in deps:
                    techs.append("React")
                if "vue" in deps:
                    techs.append("Vue")
                if "vite" in deps:
                    techs.append("Vite")
                if "electron" in deps:
                    techs.append("Electron")
                if "tailwindcss" in deps:
                    techs.append("Tailwind CSS")
                if "typescript" in deps:
                    techs.append("TypeScript")
        except (json.JSONDecodeError, OSError):
            pass

    if os.path.exists(os.path.join(project_path, "pyproject.toml")):
        techs.append("Python")
    if os.path.exists(os.path.join(project_path, "requirements.txt")):
        techs.append("Python")

    # 檢查特定檔案
    for f in os.listdir(project_path):
        if f.endswith(".py") and "Python" not in techs:
            techs.append("Python")
            break
        if f.endswith(".sln"):
            techs.append("C# / .NET")
            break
        if f.endswith(".rs") or f == "Cargo.toml":
            techs.append("Rust")
            break

    return list(set(techs))


# ─── 主掃描邏輯 ───────────────────────────────────────────────

def scan_all_projects(base_dir: str, output_path: str | None = None) -> dict:
    """掃描所有專案目錄，產生統一 JSON。"""
    projects = []

    for entry in sorted(os.listdir(base_dir)):
        project_path = os.path.join(base_dir, entry)
        if not os.path.isdir(project_path):
            continue
        if entry.startswith("."):
            continue

        print(f"  📂 掃描中：{entry} ...", end=" ")

        has_git = os.path.isdir(os.path.join(project_path, ".git"))

        # 生成專案 ID
        project_id = re.sub(r"[^\w-]", "-", entry.lower()).strip("-")

        # 收集資料
        git_url = get_git_remote(project_path) if has_git else None
        version = get_version(project_path)
        description = get_description(project_path)
        project_name = get_project_name(project_path, entry)
        status_data = parse_status_file(project_path)
        last_commit = get_last_commit_date(project_path) if has_git else None
        git_log = get_git_log(project_path) if has_git else []
        tech_stack = detect_tech_stack(project_path)

        project_data = {
            "id": project_id,
            "folder_name": entry,
            "name": project_name,
            "version": version,
            "github_url": git_url,
            "has_git": has_git,
            "tech_stack": tech_stack,
            "description": description or "尚無描述",
            "changelog": status_data["changelog"],
            "tasks": status_data["tasks"],
            "revision_history": status_data.get("revision_history", []),
            "recent_commits": git_log[:10],
            "last_commit": last_commit,
            "last_scanned": datetime.now().isoformat(),
        }

        projects.append(project_data)
        print("✅")

    output = {
        "generated_at": datetime.now().isoformat(),
        "base_dir": base_dir,
        "project_count": len(projects),
        "projects": projects,
    }

    # 確保輸出目錄存在
    if output_path is None:
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, "projects.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*50}")
    print(f"✅ 掃描完成！共 {len(projects)} 個專案")
    print(f"📄 JSON 輸出：{output_path}")
    print(f"⏰ 產生時間：{output['generated_at']}")
    print(f"{'='*50}")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="掃描所有專案資料夾並產生統一 JSON 資料"
    )
    parser.add_argument(
        "--base-dir",
        default=DEFAULT_BASE_DIR,
        help=f"專案根目錄路徑 (預設: {DEFAULT_BASE_DIR})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"JSON 輸出路徑 (預設: {DEFAULT_OUTPUT_DIR}/projects.json)",
    )
    args = parser.parse_args()

    print(f"🔍 專案監控掃描器")
    print(f"📁 掃描目錄：{args.base_dir}")
    print(f"{'='*50}\n")

    if not os.path.isdir(args.base_dir):
        print(f"❌ 錯誤：目錄不存在 — {args.base_dir}")
        sys.exit(1)

    scan_all_projects(args.base_dir, args.output)


if __name__ == "__main__":
    main()
