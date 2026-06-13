#!/usr/bin/env python3
"""
List all notebooks from NotebookLM dashboard.
Uses the existing Chrome profile for authentication.
"""

import sys
import os
import io
import json
import time
from pathlib import Path

# Force UTF-8 output on Windows
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

def main():
    from patchright.sync_api import sync_playwright

    # Try multiple possible Chrome profile locations
    profile_candidates = [
        Path(r"D:\01-Project\05-global skills\chrome_profile_notebooklm"),
        Path(r"D:\01-Project\03-modules\chrome_profile_notebooklm"),
        Path(__file__).parent.parent / "data" / "browser_state" / "browser_profile",
    ]
    
    user_data_dir = None
    for p in profile_candidates:
        if p.exists():
            user_data_dir = str(p)
            break
    
    if not user_data_dir:
        print("ERROR: No Chrome profile found for NotebookLM authentication.")
        print("Searched locations:")
        for p in profile_candidates:
            print(f"  - {p}")
        sys.exit(1)
    
    print(f"Using Chrome profile: {user_data_dir}")
    
    with sync_playwright() as p:
        # Launch with existing profile
        context = p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
                '--no-first-run',
                '--no-default-browser-check',
            ],
            viewport={'width': 1280, 'height': 720},
        )
        
        page = context.new_page()
        
        try:
            print("Navigating to NotebookLM...")
            page.goto("https://notebooklm.google.com/", wait_until="domcontentloaded", timeout=30000)
            
            # Wait for page to settle
            time.sleep(5)
            
            current_url = page.url
            print(f"Current URL: {current_url}")
            
            # Check if we're redirected to login
            if "accounts.google.com" in current_url:
                print("ERROR: Authentication required. The Chrome profile session has expired.")
                print("Please run: python scripts/run.py auth_manager.py setup")
                context.close()
                sys.exit(1)
            
            # Wait for notebooks to load
            time.sleep(3)
            
            # Try to find notebook elements on the dashboard
            # NotebookLM typically shows notebooks as cards
            notebooks = []
            
            # Strategy 1: Look for notebook cards with various selectors
            selectors_to_try = [
                'a[href*="/notebook/"]',
                '[data-notebook-id]',
                '.notebook-card',
                '.notebook-item',
                'mat-card',
                '[role="listitem"]',
                '.project-card',
                '.recent-notebook',
            ]
            
            for selector in selectors_to_try:
                elements = page.query_selector_all(selector)
                if elements:
                    print(f"Found {len(elements)} elements with selector: {selector}")
                    for el in elements:
                        title = el.get_attribute('aria-label') or el.inner_text().strip()
                        href = el.get_attribute('href') or ''
                        if title:
                            notebooks.append({
                                'title': title[:200],  # Limit length
                                'url': href if href else 'N/A',
                                'selector': selector,
                            })
                    break
            
            # Strategy 2: If no specific selectors found, get all text content and links
            if not notebooks:
                print("\nNo standard selectors found. Analyzing page content...")
                
                # Get all links that point to notebooks
                all_links = page.query_selector_all('a')
                for link in all_links:
                    href = link.get_attribute('href') or ''
                    if '/notebook/' in href:
                        text = link.inner_text().strip()
                        if text:
                            notebooks.append({
                                'title': text[:200],
                                'url': href,
                                'selector': 'a[href*=notebook]',
                            })
            
            # Strategy 3: Get page HTML snippet for debugging
            if not notebooks:
                print("\nStill no notebooks found. Dumping page structure...")
                body_text = page.inner_text('body')
                print(f"\nPage text content (first 3000 chars):\n{body_text[:3000]}")
                
                # Also get HTML structure
                body_html = page.inner_html('body')
                print(f"\nPage HTML (first 3000 chars):\n{body_html[:3000]}")
            
            # Output results
            if notebooks:
                print(f"\n{'='*60}")
                print(f"Found {len(notebooks)} notebook(s):")
                print(f"{'='*60}")
                for i, nb in enumerate(notebooks, 1):
                    print(f"\n  [{i}] {nb['title']}")
                    if nb['url'] != 'N/A':
                        url = nb['url']
                        if url.startswith('/'):
                            url = f"https://notebooklm.google.com{url}"
                        print(f"      URL: {url}")
            else:
                print("\nNo notebooks found on the dashboard.")
                
        except Exception as e:
            print(f"ERROR: {e}")
            import traceback
            traceback.print_exc()
        finally:
            context.close()

if __name__ == "__main__":
    main()
