"""Take screenshots for Lab 28 submission"""
import subprocess, os, sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

SCREENSHOTS_DIR = Path(__file__).parent.parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# ── 1. Terminal output screenshots via PIL ────────────────────────────────────

def text_to_image(text, filename, bg="#1e1e1e", fg="#d4d4d4", title=""):
    lines = text.strip().splitlines()
    font_size = 14
    padding = 20
    line_height = font_size + 4

    try:
        font = ImageFont.truetype("C:/Windows/Fonts/consola.ttf", font_size)
        title_font = ImageFont.truetype("C:/Windows/Fonts/consolab.ttf", font_size)
    except Exception:
        font = ImageFont.load_default()
        title_font = font

    max_width = max((len(l) for l in lines), default=40) * (font_size // 2 + 1) + padding * 2
    height = len(lines) * line_height + padding * 2 + (30 if title else 0)
    width = max(max_width, 600)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)

    y = padding
    if title:
        draw.text((padding, y), title, fill="#569cd6", font=title_font)
        y += 24

    for line in lines:
        color = fg
        if "[PASS]" in line:
            color = "#4ec9b0"
        elif "[FAIL]" in line:
            color = "#f44747"
        elif line.startswith("===") or "passed" in line or "Score" in line:
            color = "#dcdcaa"
        elif line.startswith("READY") or "READY" in line:
            color = "#4ec9b0"
        draw.text((padding, y), line, fill=color, font=font)
        y += line_height

    path = SCREENSHOTS_DIR / filename
    img.save(path)
    print(f"  Saved: {path}")

# Run production readiness check
print("Capturing production readiness...")
r = subprocess.run(["python", "scripts/production_readiness_check.py"],
                   capture_output=True, text=True, cwd=Path(__file__).parent.parent)
text_to_image(r.stdout, "production_readiness.png",
              title="Production Readiness Check — Lab 28")

# Run smoke tests
print("Capturing smoke tests...")
r = subprocess.run([sys.executable, "-m", "pytest", "smoke-tests/test_e2e.py", "-v", "--tb=short"],
                   capture_output=True, text=True, cwd=Path(__file__).parent.parent)
text_to_image(r.stdout + r.stderr, "smoke_tests_results.png",
              title="Smoke Tests — Lab 28")

# ── 2. Browser screenshots via Playwright ────────────────────────────────────

BROWSER_SHOTS = [
    ("http://localhost:4200", "prefect_ui.png", "Prefect UI"),
    ("http://localhost:3000", "grafana_dashboard.png", "Grafana Dashboard"),
]

print("Capturing browser screenshots...")
with sync_playwright() as p:
    browser = p.chromium.launch()
    for url, filename, label in BROWSER_SHOTS:
        try:
            page = browser.new_page(viewport={"width": 1280, "height": 800})
            page.goto(url, timeout=10000, wait_until="networkidle")
            page.wait_for_timeout(2000)
            path = str(SCREENSHOTS_DIR / filename)
            page.screenshot(path=path, full_page=False)
            print(f"  Saved: {path} ({label})")
        except Exception as e:
            print(f"  WARN: {label} — {e}")
    browser.close()

print("\nDone! Screenshots saved to screenshots/")
