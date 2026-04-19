#!/usr/bin/env python3
"""
retag_skills.py — 使用廣義標籤規則重新標記所有技能（零 API 呼叫）
目標：覆蓋率 100%（無法匹配者自動歸入 #通用工具）

直接讀取現有 skills.json，套用規則後重新輸出。
執行方式：
  python retag_skills.py
"""
import os, sys, json
from datetime import datetime

if sys.platform == "win32":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

INPUT_PATH  = r"D:\01-Project\08-監控AI各專案進度之網站\data\skills.json"
OUTPUT_PATH = INPUT_PATH

# ─── 全面廣義標籤規則（25 大類 + #通用工具兜底）──────────────────────────
TAG_RULES = [
    {
        "tag": "#前端設計",
        "keywords": [
            "frontend", "front-end", "react", "vue", "angular", "svelte",
            "next.js", "nextjs", "web component", "landing page", "dashboard",
            "html", "tailwind", "shadcn", "ui component", "design system",
            "web ui", "web app", "web artifact", "styling", "responsive",
            "page layout", "css", "kpi dashboard", "astro", "ui-page",
            "ui-component", "ui-pattern", "ui-tokens", "ui-setup", "ui-a11y",
            "makepad", "avalonia", "ux-copy", "ux-feedback", "ux-flow",
            "ux-audit", "ux-persuasion", "baseline-ui", "rayden", "stitch",
            "hig-", "chat-widget", "chrome-extension", "browser-extension",
            "core-components", "app-builder", "remotion",
        ],
    },
    {
        "tag": "#後端開發",
        "keywords": [
            "backend", "back-end", "fastapi", "api route", "endpoint",
            "uvicorn", "express", "rest api", "graphql", "grpc",
            "node.js", "nodejs", "bun", "rails", "django", "flask",
            "nestjs", "hono", "laravel", "server action", "trpc",
            "asp.net", "spring", "server-side", "async-python",
            "fp-async", "fp-errors", "fp-react", "fp-backend",
            "dbos-", "convex",
        ],
    },
    {
        "tag": "#資料庫",
        "keywords": [
            "database", "sql", "postgres", "postgresql", "mysql", "mongodb",
            "prisma", "drizzle", "orm", "redis", "sqlite", "nosql",
            "supabase", "neon", "cockroach", "firestore", "dynamodb",
            "vector database", "migration", "clickhouse", "cqrs",
            "event-store", "dbos",
        ],
    },
    {
        "tag": "#雲端服務",
        "keywords": [
            "aws", "azure", "gcp", "google cloud", "cloud", "serverless",
            "lambda", "s3 bucket", "cloudfront", "vercel", "netlify",
            "render", "fly.io", "railway", "heroku", "appdeploy",
        ],
    },
    {
        "tag": "#DevOps",
        "keywords": [
            "devops", "ci/cd", "cicd", "github action", "gitlab ci",
            "docker", "kubernetes", "k8s", "helm", "terraform", "ansible",
            "monitoring", "observability", "deployment", "pipeline",
            "infrastructure", "iac", "gitops", "build-system", "bazel",
            "incident-responder", "incident-response", "on-call",
            "axiom", "prometheus", "grafana", "datadog", "sentry",
            "appdeploy",
        ],
    },
    {
        "tag": "#安全稽核",
        "keywords": [
            "security", "penetration", "pentest", "audit", "vulnerability",
            "exploit", "owasp", "authentication", "authorization",
            "encryption", "zero trust", "iam", "compliance", "hacking",
            "red team", "malware", "forensic", "sast", "dast",
            "burpsuite", "metasploit", "shodan", "ffuf", "bug-hunter",
            "privilege-escalation", "attack-tree", "constant-time",
            "cred-omega", "aws-iam", "aws-security", "django-access",
            "secrets-management", "varlock",
        ],
    },
    {
        "tag": "#AI工具",
        "keywords": [
            "claude", "anthropic", "llm", "gemini", "notebooklm", "openai",
            "gpt", "chatgpt", "ai model", "prompt", "langchain",
            "llamaindex", "hugging face", "transformers", "embedding",
            "rag", "fine-tun", "vector search", "fal-", "imagen",
            "computer-vision", "evaluation", "ai-studio", "ai-ml",
            "ai-analyzer", "ai-product", "ai-wrapper", "ai-native",
            "gemini-api", "claude-api", "bdistill", "llm-app",
            "context-agent", "context-compression", "context-window",
            "context-optimization",
        ],
    },
    {
        "tag": "#AI代理人",
        "keywords": [
            "agent", "crewai", "multi-agent", "autonomous", "agentic",
            "orchestrat", "langgraph", "autogen", "agent framework",
            "tool use", "conductor-", "bdi-mental", "behavioral-modes",
            "agent-evaluation", "agent-memory", "agent-tool",
            "subagent", "dispatching", "pipecat", "voice-agent",
        ],
    },
    {
        "tag": "#行動應用",
        "keywords": [
            "ios", "android", "mobile", "swift", "swiftui", "kotlin",
            "flutter", "react native", "expo", "jetpack compose",
            "app store", "play store", "cross-platform",
            "hig-", "macos-menubar", "macos-spm",
        ],
    },
    {
        "tag": "#測試除錯",
        "keywords": [
            "testing", "playwright", "vitest", "jest", "pytest",
            "debug", "screenshot", "browser test", "e2e", "qa",
            "unit test", "integration test", "visual regression",
            "test-driven", "tdd", "bdd", "mock", "debugger",
            "error-detective", "error-diagnos", "error-debug",
            "bug-hunter", "systematic-debug", "phase-gated",
        ],
    },
    {
        "tag": "#文件處理",
        "keywords": [
            "pdf", "word", "docx", "pptx", "presentation", "slide",
            "spreadsheet", "xlsx", "csv", "libreoffice", "excel",
            "powerpoint", "latex", "docx-official", "pptx-official",
            "pdf-official", "xlsx-official",
        ],
    },
    {
        "tag": "#自動化",
        "keywords": [
            "automation", "automate", "cron", "trigger", "zapier",
            "make.com", "n8n", "inngest", "batch", "schedule",
            "webhook", "no-code", "apify-", "rpa",
            "gmail-automation", "slack-automation", "discord-automation",
            "hubspot-automation", "salesforce-automation",
        ],
    },
    {
        "tag": "#行銷分析",
        "keywords": [
            "seo", "analytics", "marketing", "conversion", "cro",
            "campaign", "email marketing", "social media", "ads",
            "audience", "growth", "copywriting", "a/b test", "funnel",
            "content-strategy", "content-creator", "cold-email",
            "lead-generation", "churn-prevention", "competitor",
            "brand-perception", "awareness-stage", "pitch-psychologist",
            "subject-line", "headline-psychologist", "geo-fundamental",
            "apify-market", "apify-competitor", "apify-influencer",
            "apify-trend", "apify-brand", "apify-audience",
            "page-cro", "popup-cro", "paywall-upgrade-cro",
        ],
    },
    {
        "tag": "#資料處理",
        "keywords": [
            "data pipeline", "etl", "pandas", "spark", "data warehouse",
            "dbt", "data transformation", "dataset", "data engineer",
            "polars", "numpy", "dataframe", "airflow", "dag",
            "biopython", "astropy", "scanpy", "statsmodel",
            "data-storytelling", "data-scientist",
        ],
    },
    {
        "tag": "#視覺設計",
        "keywords": [
            "visual", "poster", "canvas", "brand guideline", "animation",
            "generative art", "figma", "illustration", "color palette",
            "theme", "magic ui", "motion", "three.js", "threejs",
            "algorithmic-art", "design-spells", "vizcom", "magic-animator",
            "animejs", "shader", "spline-3d",
        ],
    },
    {
        "tag": "#系統架構",
        "keywords": [
            "architecture", "c4-", "cqrs", "ddd-", "domain-driven",
            "event-sourcing", "saga-orchestration", "microservices",
            "distributed", "system design", "architect-review",
            "senior-architect", "blueprint", "api-patterns",
        ],
    },
    {
        "tag": "#系統工具",
        "keywords": [
            "linux", "bash", "shell", "powershell", "busybox",
            "tmux", "git-", "posix", "windows-shell", "cli",
            "terminal", "os-script", "gdb-cli", "build",
            "commit", "create-branch", "create-pr", "create-issue",
            "git-push", "git-hook", "git-pr-workflow",
        ],
    },
    {
        "tag": "#商業分析",
        "keywords": [
            "startup", "business analyst", "market sizing", "product manager",
            "product inventor", "product-manager", "financial-model",
            "competitive-landscape", "competitor-alternatives",
            "team-composition", "risk-manager", "business-case",
            "financial-projection", "market-opportunity",
            "pricing-strategy", "monetization", "revops",
            "leiloeiro", "advogado", "lex",
        ],
    },
    {
        "tag": "#程式語言",
        "keywords": [
            "c-pro", "cpp-pro", "csharp-pro", "golang", "rust-pro",
            "julia-pro", "haskell-pro", "scala-pro", "java-pro",
            "python-pro", "ruby-pro", "elixir-pro", "php-pro",
            "kotlin", "typescript-pro", "typescript-expert",
            "typescript-advanced", "javascript-pro", "javascript-mastery",
            "fp-ts", "fp-option", "fp-either", "fp-pipe",
        ],
    },
    {
        "tag": "#系統整合",
        "keywords": [
            "mcp server", "model context protocol", "sdk integration",
            "api gateway", "connector", "external service", "odoo-",
            "erp", "salesforce-development", "shopify-development",
            "stripe-integration", "payment-integration", "plaid",
            "twilio", "segment-cdp",
        ],
    },
    {
        "tag": "#專案管理",
        "keywords": [
            "project status", "project monitor", "version control",
            "changelog", "roadmap", "sprint", "agile", "scrum",
            "linear", "jira", "asana", "github issue", "conductor-",
            "concise-planning", "closed-loop", "writing-plans",
            "planning-with-files", "track-management",
        ],
    },
    {
        "tag": "#溝通協作",
        "keywords": [
            "internal comm", "documentation", "proposal", "wiki",
            "knowledge base", "co-author", "writing guide", "newsletter",
            "report writing", "slack", "notion", "confluence",
            "obsidian", "citation-management", "copy-editing",
            "blog-writing", "beautiful-prose", "avoid-ai-writing",
            "team-collaboration", "customer-support", "daily-news",
        ],
    },
    {
        "tag": "#程式碼品質",
        "keywords": [
            "code generate", "scaffold", "boilerplate", "code template",
            "refactor", "code review", "code quality", "linting",
            "code-reviewer", "code-simplifier", "clean-code",
            "simplify-code", "tech-debt", "codebase-cleanup",
            "receiving-code-review", "differential-review",
            "vibe-code-auditor", "code-refactor",
        ],
    },
    {
        "tag": "#心智圖",
        "keywords": [
            "mind map", "mindmap", "xmind", "diagram", "brainstorm",
            "mermaid", "visual thinking", "concept map", "c4-container",
            "c4-component", "c4-context", "c4-code",
        ],
    },
    {
        "tag": "#技能開發",
        "keywords": [
            "skill creator", "skill builder", "create skill",
            "skill-creator", "skill-router", "skill-scanner",
            "skill-developer", "skill-writer", "skill-optimizer",
            "skill-improver", "writing-skills", "manage-skills",
            "cc-skill-", "andruia-", "10-andruia", "20-andruia",
        ],
    },
]

FALLBACK_TAG = "#通用工具"  # 無法匹配任何規則時使用


def auto_tag(name: str, description: str) -> list:
    text = f"{name} {description}".lower()
    tags = []
    for rule in TAG_RULES:
        for kw in rule["keywords"]:
            if kw.lower() in text:
                tags.append(rule["tag"])
                break
    if not tags:
        tags = [FALLBACK_TAG]
    return sorted(set(tags))


def main():
    print(f"載入 {INPUT_PATH} ...")
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    skills = data.get("skills", [])
    total = len(skills)
    changed = 0
    fallback_count = 0

    print(f"共 {total} 個技能，套用廣義標籤規則（含 #通用工具 兜底）...\n")

    for skill in skills:
        old_tags = skill.get("tags", [])
        new_tags = auto_tag(skill.get("name", ""), skill.get("description", ""))
        skill["tags"] = new_tags
        if set(new_tags) != set(old_tags):
            changed += 1
        if new_tags == [FALLBACK_TAG]:
            fallback_count += 1

    # 重建 tag_index
    tag_index: dict = {}
    for skill in skills:
        for tag in skill.get("tags", []):
            tag_index.setdefault(tag, []).append(skill["name"])
    tag_index = dict(sorted(tag_index.items(), key=lambda x: -len(x[1])))

    all_tags = set()
    for s in skills:
        all_tags.update(s.get("tags", []))

    data["tag_index"] = tag_index
    data["stats"]["total_tags"] = len(all_tags)
    data["stats"]["tags_list"] = sorted(all_tags)
    data["retagged_at"] = datetime.now().isoformat()

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    tagged_count = sum(1 for s in skills if s.get("tags"))
    meaningful = sum(1 for s in skills if s.get("tags") and s["tags"] != [FALLBACK_TAG])

    print(f"✅ 重新標籤完成！")
    print(f"  總技能數:       {total}")
    print(f"  有標籤 (100%):  {tagged_count}")
    print(f"  有意義標籤:     {meaningful} ({meaningful*100//total}%)")
    print(f"  #通用工具 兜底: {fallback_count}")
    print(f"  更新技能數:     {changed}")
    print(f"\n標籤分佈:")
    for tag, names in tag_index.items():
        bar = "█" * min(len(names) // 5, 30)
        print(f"  {tag:<12}: {len(names):>4}  {bar}")
    print(f"\n輸出至: {OUTPUT_PATH}")

    # ─── 同步產生輕量版 skills_slim.json（前端載入用）────────────────
    slim_output = OUTPUT_PATH.replace("data\\skills.json", "public\\data\\skills_slim.json")
    slim_skills = []
    for s in skills:
        slim_skills.append({
            "name":         s.get("name", ""),
            "display_name": s.get("display_name", ""),
            "description":  s.get("description", ""),
            "summary":      s.get("summary", ""),
            "tags":         s.get("tags", []),
        })
    slim_data = {
        "generated_at": data.get("generated_at", ""),
        "stats":        data["stats"],
        "skills":       slim_skills,
        "workflows":    [{"name": w.get("name"), "display_name": w.get("display_name"), "content": w.get("content", "")}
                         for w in data.get("workflows", [])],
        "tag_index":    tag_index,
    }
    with open(slim_output, "w", encoding="utf-8") as f:
        json.dump(slim_data, f, ensure_ascii=False, separators=(",", ":"))

    slim_kb = os.path.getsize(slim_output) // 1024
    full_mb = os.path.getsize(OUTPUT_PATH) / 1024 / 1024
    reduction = 100 - int(slim_kb * 100 / (full_mb * 1024))
    print(f"\n⚡ 輕量版同步: {slim_kb} KB（完整版 {full_mb:.1f} MB，縮減 {reduction}%）")
    print(f"   路徑: {slim_output}")


if __name__ == "__main__":
    main()
