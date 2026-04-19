#!/usr/bin/env python3
"""
sync_to_website.py — 執行完整掃描並將 JSON 同步至監控網站

使用方式：
  python sync_to_website.py                     # 掃描專案 + 技能 + 工作流
  python sync_to_website.py --generate-status    # 同時為所有專案產生 PROJECT_STATUS.md
  python sync_to_website.py --projects-only      # 只掃描專案
  python sync_to_website.py --skills-only        # 只掃描技能與工作流
"""

import os
import sys
import json
import argparse
from datetime import datetime

# ─── Windows 終端 UTF-8 修正 ───
if sys.platform == "win32":
    import io
    if not isinstance(sys.stdout, io.TextIOWrapper) or sys.stdout.encoding != "utf-8":
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass

# 載入同級腳本
sys.path.insert(0, os.path.dirname(__file__))
from scan_projects import scan_all_projects, DEFAULT_BASE_DIR, DEFAULT_OUTPUT_DIR
from scan_skills import scan_all as scan_all_skills_and_workflows
from generate_status import generate_status


WEBSITE_PROJECT_DIR = os.path.join(DEFAULT_BASE_DIR, "08-監控AI各專案進度之網站")
WEBSITE_DATA_DIR = os.path.join(WEBSITE_PROJECT_DIR, "data")


def sync_to_website(
    base_dir: str = DEFAULT_BASE_DIR,
    generate_all_status: bool = False,
    projects_only: bool = False,
    skills_only: bool = False,
) -> None:
    """執行完整掃描並同步至網站。"""

    print(f"{'='*60}")
    print(f"  全能 AI 互動網站 — 資料同步")
    print(f"{'='*60}")
    print(f"  專案根目錄：{base_dir}")
    print(f"  網站目錄：{WEBSITE_PROJECT_DIR}")
    print(f"  模式：{'僅專案' if projects_only else '僅技能' if skills_only else '完整掃描'}")
    print(f"{'='*60}\n")

    projects_result = None
    skills_result = None

    # ─── Phase 0: 產生 PROJECT_STATUS.md（可選）───
    if generate_all_status and not skills_only:
        print("[Phase 0] 為所有專案產生 PROJECT_STATUS.md")
        print("-" * 40)
        for entry in sorted(os.listdir(base_dir)):
            project_path = os.path.join(base_dir, entry)
            if os.path.isdir(project_path) and not entry.startswith("."):
                generate_status(project_path, force=False)
        print()

    # ─── Phase 1: 掃描專案 ───
    if not skills_only:
        print("[Phase 1] 掃描所有專案 (AI 專案呈現模組)")
        print("-" * 40)
        output_path = os.path.join(WEBSITE_DATA_DIR, "projects.json")
        projects_result = scan_all_projects(base_dir, output_path)
        print()

    # ─── Phase 2: 掃描技能 & 工作流 ───
    if not projects_only:
        print("[Phase 2] 掃描全域技能 & 工作流 (技能呈現模組 + 工作流模組)")
        print("-" * 40)
        skills_output_path = os.path.join(WEBSITE_DATA_DIR, "skills.json")
        skills_result = scan_all_skills_and_workflows(output_path=skills_output_path)
        print()

    # ─── Phase 3: 產生同步報告 ───
    print("[Phase 3] 產生同步報告")
    print("-" * 40)

    report = {
        "sync_time": datetime.now().isoformat(),
        "sync_mode": "projects_only" if projects_only else "skills_only" if skills_only else "full",
    }

    if projects_result:
        report["projects"] = {
            "total": projects_result["project_count"],
            "with_git": sum(1 for p in projects_result["projects"] if p.get("has_git")),
            "with_status_md": sum(
                1
                for p in projects_result["projects"]
                if os.path.exists(
                    os.path.join(base_dir, p["folder_name"], "PROJECT_STATUS.md")
                )
            ),
            "summary": [
                {
                    "name": p["name"],
                    "version": p["version"],
                    "has_git": p["has_git"],
                    "tech_stack": p.get("tech_stack", []),
                }
                for p in projects_result["projects"]
            ],
        }

    if skills_result:
        report["skills"] = {
            "total": skills_result["stats"]["total_skills"],
            "total_tags": skills_result["stats"]["total_tags"],
            "tags": skills_result["stats"]["tags_list"],
        }
        report["workflows"] = {
            "total": skills_result["stats"]["total_workflows"],
        }

    # 寫入報告
    report_path = os.path.join(WEBSITE_DATA_DIR, "sync_report.json")
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    # ─── 輸出摘要 ───
    print(f"\n{'='*60}")
    print(f"  同步完成！")
    print(f"{'='*60}")

    if projects_result:
        print(f"  [專案] 總數：{report['projects']['total']}")
        print(f"  [專案] 有 Git：{report['projects']['with_git']}")
        print(f"  [專案] 有 STATUS.md：{report['projects']['with_status_md']}")

    if skills_result:
        print(f"  [技能] 總數：{report['skills']['total']}")
        print(f"  [技能] 標籤數：{report['skills']['total_tags']}")
        print(f"  [工作流] 總數：{report['workflows']['total']}")

    print(f"  [報告] {report_path}")
    print(f"  [時間] {report['sync_time']}")
    print(f"{'='*60}")


def main():
    parser = argparse.ArgumentParser(
        description="執行完整掃描並將資料同步至監控網站"
    )
    parser.add_argument(
        "--base-dir",
        default=DEFAULT_BASE_DIR,
        help=f"專案根目錄路徑 (預設: {DEFAULT_BASE_DIR})",
    )
    parser.add_argument(
        "--generate-status",
        action="store_true",
        help="同時為所有專案產生 PROJECT_STATUS.md（不覆蓋已存在的）",
    )
    parser.add_argument(
        "--projects-only",
        action="store_true",
        help="只掃描專案，不掃描技能與工作流",
    )
    parser.add_argument(
        "--skills-only",
        action="store_true",
        help="只掃描技能與工作流，不掃描專案",
    )
    args = parser.parse_args()

    if args.projects_only and args.skills_only:
        print("[!] 不可同時指定 --projects-only 和 --skills-only")
        sys.exit(1)

    sync_to_website(args.base_dir, args.generate_status, args.projects_only, args.skills_only)


if __name__ == "__main__":
    main()
