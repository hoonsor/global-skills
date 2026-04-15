#!/usr/bin/env python3
r"""
scan_skills.py — 掃描 Antigravity 所有全域技能與工作流，產出統一 JSON
供監控網站的「全域技能呈現模組」與「工作流呈現模組」介接使用。

使用方式：
  python scan_skills.py
  python scan_skills.py --skills-dir "C:\Users\hoonsor\.gemini\antigravity\skills"
  python scan_skills.py --output "D:\01-Project\08-監控AI各專案進度之網站\data\skills.json"

產出：
  - skills.json: 包含所有技能與工作流資訊、自動產生的功能標籤
"""

import os
import sys
import json
import re
import argparse
import codecs
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
            pass  # 已被其他模組設定過

# ─── 預設路徑 ───────────────────────────────────────────────────
DEFAULT_SKILLS_DIR = r"C:\Users\hoonsor\.gemini\antigravity\skills"
DEFAULT_WORKFLOWS_DIR = r"C:\Users\hoonsor\.gemini\antigravity\global_workflows"
DEFAULT_OUTPUT_DIR = os.path.join(r"D:\01-Project", "08-監控AI各專案進度之網站", "data")

# ─── 功能標籤映射表 ───────────────────────────────────────────────
# 標籤只根據 name + description 匹配（不掃描 body 避免過度匹配）
# 使用精確的多詞詞組避免泛用關鍵詞誤匹配
TAG_RULES = [
    {
        "tag": "#前端設計",
        "keywords": [
            "frontend", "front-end", "web component", "landing page",
            "dashboard", "react component", "html/css", "web ui",
            "styling", "beautif", "web app", "web artifact",
            "shadcn", "tailwind",
        ],
    },
    {
        "tag": "#後端開發",
        "keywords": [
            "backend", "back-end", "fastapi", "api route",
            "endpoint", "uvicorn", "express server",
        ],
    },
    {
        "tag": "#文件處理",
        "keywords": [
            ".pdf", "pdf file", "word doc", ".docx", ".pptx", "presentation",
            "slide deck", "spreadsheet", ".xlsx", ".csv", ".tsv",
            "word document",
        ],
    },
    {
        "tag": "#視覺設計",
        "keywords": [
            "visual art", "poster", "canvas-design", "algorithmic art",
            "brand color", "brand guideline", "gif", "animation",
            "theme-factory", "theme styling", "design quality",
            "generative art",
        ],
    },
    {
        "tag": "#資料處理",
        "keywords": [
            "spreadsheet", ".xlsx", ".csv", "tabular data",
            "extract table", "data file",
        ],
    },
    {
        "tag": "#系統整合",
        "keywords": [
            "mcp server", "mcp-builder", "model context protocol",
            "external service", "api integration",
        ],
    },
    {
        "tag": "#AI工具",
        "keywords": [
            "claude api", "anthropic sdk", "notebooklm",
            "agent sdk", "claude_agent",
        ],
    },
    {
        "tag": "#專案管理",
        "keywords": [
            "project status", "project monitor", "scan project",
            "version control", "changelog",
        ],
    },
    {
        "tag": "#測試除錯",
        "keywords": [
            "webapp-testing", "playwright", "browser test",
            "visual regression", "screenshot", "browser log",
        ],
    },
    {
        "tag": "#心智圖",
        "keywords": [
            "mind map", "mindmap", "xmind", "brainstorm diagram",
        ],
    },
    {
        "tag": "#溝通協作",
        "keywords": [
            "internal comm", "status report", "newsletter",
            "co-author", "doc-coauthoring", "writing doc",
            "internal-comms",
        ],
    },
    {
        "tag": "#技能開發",
        "keywords": [
            "skill-creator", "create skill", "skill performance",
            "eval", "benchmark skill",
        ],
    },
]

def translate_to_zh_tw(text: str) -> str:
    """使用免費的 Google API 進行英翻中。"""
    if not text or not text.strip() or len(text) < 2:
        return text
    try:
        url = "https://translate.googleapis.com/translate_a/single?client=gtx&sl=auto&tl=zh-TW&dt=t&q=" + urllib.parse.quote(text)
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            result = json.loads(response.read().decode('utf-8'))
            val = "".join([sentence[0] for sentence in result[0] if sentence[0]])
            time.sleep(0.1) # 避免請求過快被鎖
            return val
    except Exception as e:
        # 出錯就退回原本的字串
        return text

def parse_yaml_frontmatter(content: str) -> dict:
    """解析 YAML frontmatter（簡易版，不依賴 PyYAML）。"""
    frontmatter = {}
    if not content.startswith("---"):
        return frontmatter

    # 找到結束的 ---
    end_idx = content.find("---", 3)
    if end_idx == -1:
        return frontmatter

    yaml_block = content[3:end_idx].strip()
    current_key = None
    current_value_lines = []

    for line in yaml_block.split("\n"):
        # 處理多行值（使用 > 或 | 語法或是引號跨行）
        if re.match(r"^\w[\w-]*\s*:", line):
            # 儲存前一個 key
            if current_key:
                frontmatter[current_key] = " ".join(current_value_lines).strip()
                current_value_lines = []

            match = re.match(r"^([\w-]+)\s*:\s*(.*)", line)
            if match:
                current_key = match.group(1)
                val = match.group(2).strip()
                # 移除引號
                if val.startswith('"') and val.endswith('"'):
                    val = val[1:-1]
                elif val.startswith("'") and val.endswith("'"):
                    val = val[1:-1]
                # 如果是 > 或 | 表示接下來是多行內容
                if val in (">", "|", ">-", "|-"):
                    current_value_lines = []
                elif val:
                    current_value_lines = [val]
                else:
                    current_value_lines = []
        else:
            # 續行
            stripped = line.strip()
            if stripped:
                current_value_lines.append(stripped)

    # 儲存最後一個 key
    if current_key:
        frontmatter[current_key] = " ".join(current_value_lines).strip()

    return frontmatter


def get_body_content(content: str) -> str:
    """取得 frontmatter 之後的 Markdown body。"""
    if not content.startswith("---"):
        return content

    end_idx = content.find("---", 3)
    if end_idx == -1:
        return content

    return content[end_idx + 3:].strip()


def auto_generate_tags(name: str, description: str, body: str = "") -> list[str]:
    """根據 name + description 自動產生功能性標籤。
    
    注意：只搜索 name + description，不搜索 body，
    避免因 body 中出現常見詞彙而產生過多不精確的標籤。
    """
    search_text = f"{name} {description}".lower()
    tags = []

    for rule in TAG_RULES:
        for keyword in rule["keywords"]:
            if keyword.lower() in search_text:
                tags.append(rule["tag"])
                break  # 一個規則只需匹配一次

    return sorted(set(tags))


def get_skill_structure(skill_path: str) -> dict:
    """偵測技能的檔案結構。"""
    structure = {
        "has_scripts": os.path.isdir(os.path.join(skill_path, "scripts")),
        "has_references": os.path.isdir(os.path.join(skill_path, "references")),
        "has_templates": os.path.isdir(os.path.join(skill_path, "templates")),
        "has_resources": os.path.isdir(os.path.join(skill_path, "resources")),
        "has_assets": os.path.isdir(os.path.join(skill_path, "assets")),
        "has_examples": os.path.isdir(os.path.join(skill_path, "examples")),
        "has_evals": os.path.isdir(os.path.join(skill_path, "evals")),
    }

    # 計算檔案總數與大小
    total_files = 0
    total_size = 0
    for root, dirs, files in os.walk(skill_path):
        # 排除 node_modules, .venv, .git 等
        dirs[:] = [d for d in dirs if d not in ("node_modules", ".venv", ".git", "__pycache__", ".next")]
        for f in files:
            filepath = os.path.join(root, f)
            total_files += 1
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                pass

    structure["total_files"] = total_files
    structure["total_size_kb"] = round(total_size / 1024, 1)

    return structure


def get_skill_summary(body: str) -> str:
    """從 body 內容提取技能功能概述（第一段非標題文字）。"""
    lines = body.split("\n")
    summary_lines = []
    found_content = False

    for line in lines:
        stripped = line.strip()
        if not stripped:
            if found_content and summary_lines:
                break
            continue
        if stripped.startswith("#"):
            if found_content and summary_lines:
                break
            continue
        found_content = True
        summary_lines.append(stripped)

    result = " ".join(summary_lines)
    # 截斷過長的概述
    if len(result) > 300:
        result = result[:297] + "..."
    return result


def scan_skill(skill_path: str) -> dict | None:
    """掃描單一技能資料夾，回傳結構化資料。"""
    skill_md = os.path.join(skill_path, "SKILL.md")
    if not os.path.exists(skill_md):
        return None

    try:
        with open(skill_md, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    frontmatter = parse_yaml_frontmatter(content)
    name = frontmatter.get("name", os.path.basename(skill_path))
    
    if "description" in frontmatter:
        print(f"正在翻譯技能/工作流敘述: {name}")
        frontmatter["description"] = translate_to_zh_tw(frontmatter["description"])
        
    description = frontmatter.get("description", "No description provided.")
    
    # 解析 body 並取得與翻譯 summary
    body = get_body_content(content)
    summary = get_skill_summary(body)
    if summary and "No summary" not in summary:
        summary = translate_to_zh_tw(summary)

    # 自動產生功能性標籤
    tags = auto_generate_tags(name, description, body)

    # 偵測結構
    structure = get_skill_structure(skill_path)

    return {
        "name": name,
        "display_name": name.replace("-", " ").title(),
        "description": description,
        "summary": summary if summary != description else "",
        "tags": tags,
        "path": skill_path,
        "structure": structure,
        "frontmatter": {
            k: v for k, v in frontmatter.items()
            if k not in ("name", "description")
        },
        "skill_md_lines": len(content.split("\n")),
        "last_modified": datetime.fromtimestamp(
            os.path.getmtime(skill_md)
        ).isoformat(),
    }


def scan_workflow(workflow_path: str) -> dict | None:
    """掃描單一工作流檔案，回傳結構化資料。"""
    if not os.path.exists(workflow_path):
        return None

    try:
        with open(workflow_path, "r", encoding="utf-8") as f:
            content = f.read()
    except OSError:
        return None

    frontmatter = parse_yaml_frontmatter(content)
    body = get_body_content(content)

    filename = os.path.basename(workflow_path)
    name = os.path.splitext(filename)[0]

    return {
        "name": name,
        "display_name": name.replace("-", " ").replace("_", " ").title(),
        "description": frontmatter.get("description", ""),
        "content": body,  # 工作流的完整內容（供網站呈現程式碼區塊）
        "path": workflow_path,
        "filename": filename,
        "last_modified": datetime.fromtimestamp(
            os.path.getmtime(workflow_path)
        ).isoformat(),
    }


def scan_all_skills(skills_dir: str) -> list[dict]:
    """掃描所有技能資料夾。"""
    skills = []

    if not os.path.isdir(skills_dir):
        print(f"  [!] 技能目錄不存在：{skills_dir}")
        return skills

    for entry in sorted(os.listdir(skills_dir)):
        skill_path = os.path.join(skills_dir, entry)
        if not os.path.isdir(skill_path):
            continue
        if entry.startswith("."):
            continue

        print(f"  [技能] 掃描中：{entry} ...", end=" ")

        skill_data = scan_skill(skill_path)
        if skill_data:
            skills.append(skill_data)
            tag_str = ", ".join(skill_data["tags"]) if skill_data["tags"] else "無標籤"
            print(f"OK ({tag_str})")
        else:
            print("跳過 (無 SKILL.md)")

    return skills


def scan_all_workflows(workflows_dir: str) -> list[dict]:
    """掃描所有工作流檔案。"""
    workflows = []

    if not os.path.isdir(workflows_dir):
        print(f"  [!] 工作流目錄不存在：{workflows_dir}")
        return workflows

    for entry in sorted(os.listdir(workflows_dir)):
        if not entry.endswith(".md"):
            continue
        if entry.startswith("."):
            continue

        workflow_path = os.path.join(workflows_dir, entry)
        print(f"  [工作流] 掃描中：{entry} ...", end=" ")

        wf_data = scan_workflow(workflow_path)
        if wf_data:
            workflows.append(wf_data)
            print("OK")
        else:
            print("跳過")

    return workflows


def generate_tag_index(skills: list[dict]) -> dict:
    """產生標籤索引，方便前端檢索。"""
    tag_index = {}
    for skill in skills:
        for tag in skill.get("tags", []):
            if tag not in tag_index:
                tag_index[tag] = []
            tag_index[tag].append(skill["name"])

    # 按技能數量排序
    return dict(sorted(tag_index.items(), key=lambda x: -len(x[1])))


def scan_all(
    skills_dir: str = DEFAULT_SKILLS_DIR,
    workflows_dir: str = DEFAULT_WORKFLOWS_DIR,
    output_path: str | None = None,
) -> dict:
    """執行完整掃描，產出統一 JSON。"""

    print(f"{'='*60}")
    print(f"  Antigravity 全域技能 & 工作流掃描器")
    print(f"{'='*60}")
    print(f"  技能目錄：{skills_dir}")
    print(f"  工作流目錄：{workflows_dir}")
    print(f"{'='*60}\n")

    # 掃描技能
    print("[Phase 1] 掃描全域技能")
    print("-" * 40)
    skills = scan_all_skills(skills_dir)

    # 掃描工作流
    print(f"\n[Phase 2] 掃描全域工作流")
    print("-" * 40)
    workflows = scan_all_workflows(workflows_dir)

    # 產生標籤索引
    tag_index = generate_tag_index(skills)

    # 統計
    all_tags = set()
    for s in skills:
        all_tags.update(s.get("tags", []))

    output = {
        "generated_at": datetime.now().isoformat(),
        "skills_dir": skills_dir,
        "workflows_dir": workflows_dir,
        "stats": {
            "total_skills": len(skills),
            "total_workflows": len(workflows),
            "total_tags": len(all_tags),
            "tags_list": sorted(all_tags),
        },
        "skills": skills,
        "workflows": workflows,
        "tag_index": tag_index,
    }

    # 輸出 JSON
    if output_path is None:
        output_path = os.path.join(DEFAULT_OUTPUT_DIR, "skills.json")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"\n{'='*60}")
    print(f"  掃描完成！")
    print(f"  技能數量：{len(skills)}")
    print(f"  工作流數量：{len(workflows)}")
    print(f"  標籤總數：{len(all_tags)}")
    print(f"  JSON 輸出：{output_path}")
    print(f"  產生時間：{output['generated_at']}")
    print(f"{'='*60}")

    return output


def main():
    parser = argparse.ArgumentParser(
        description="掃描 Antigravity 全域技能與工作流，產出統一 JSON"
    )
    parser.add_argument(
        "--skills-dir",
        default=DEFAULT_SKILLS_DIR,
        help=f"技能目錄路徑 (預設: {DEFAULT_SKILLS_DIR})",
    )
    parser.add_argument(
        "--workflows-dir",
        default=DEFAULT_WORKFLOWS_DIR,
        help=f"工作流目錄路徑 (預設: {DEFAULT_WORKFLOWS_DIR})",
    )
    parser.add_argument(
        "--output",
        default=None,
        help=f"JSON 輸出路徑 (預設: {DEFAULT_OUTPUT_DIR}/skills.json)",
    )
    args = parser.parse_args()

    scan_all(args.skills_dir, args.workflows_dir, args.output)


if __name__ == "__main__":
    main()
