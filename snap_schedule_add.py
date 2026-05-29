# -*- coding: utf-8 -*-
"""Capture schedule/add with a search query to avoid loading 1115 courses."""
import os, sys, django
from pathlib import Path

os.chdir("D:/مهم/ACDC_FINAL-main")
sys.path.insert(0, "D:/مهم/ACDC_FINAL-main")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "acdc_config.settings")
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
User = get_user_model()

admin = User.objects.filter(is_superuser=True).first()
c = Client()
c.force_login(admin)
sid = c.cookies["sessionid"].value

from playwright.sync_api import sync_playwright

BASE = "http://127.0.0.1:8000"
OUT_D = Path("screenshots/desktop")
OUT_M = Path("screenshots/mobile")

with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for vp, out_dir in [
        ({"width":1920,"height":1080}, OUT_D),
        ({"width":390,"height":844},   OUT_M),
    ]:
        ctx = browser.new_context(viewport=vp, permissions=[])
        ctx.add_cookies([{"name":"sessionid","value":sid,"domain":"127.0.0.1","path":"/"}])
        page = ctx.new_page()
        # Use search query so only ~10 courses load
        page.goto(BASE + "/schedule/add/?course_q=computer", wait_until="domcontentloaded", timeout=30000)
        try: page.wait_for_load_state("networkidle", timeout=8000)
        except: pass
        out = out_dir / "35_schedule_add.png"
        page.screenshot(path=str(out), full_page=False, timeout=20000)
        print(f"OK {vp['width']}x{vp['height']} -> {out.stat().st_size//1024} KB")
        ctx.close()
    browser.close()

print("Done.")
