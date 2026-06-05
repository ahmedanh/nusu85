# -*- coding: utf-8 -*-
import sys
import time
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(viewport={"width": 1440, "height": 900})
    page = ctx.new_page()

    # Unregister any service workers first
    page.goto("http://localhost:8000/attendance/login/", wait_until="domcontentloaded", timeout=15000)

    # Get CSRF token
    csrf = page.evaluate("() => document.querySelector('input[name=csrfmiddlewaretoken]').value")
    print("CSRF:", csrf[:10])

    # POST login via fetch from within the page (avoids SW network_only issues)
    result = page.evaluate("""async (csrf) => {
        const fd = new FormData();
        fd.append('csrfmiddlewaretoken', csrf);
        fd.append('username', 'admin');
        fd.append('password', 'admin123');
        const r = await fetch('/attendance/login/', {
            method: 'POST',
            body: fd,
            credentials: 'include',
            redirect: 'follow'
        });
        return {status: r.status, url: r.url};
    }""", csrf)
    print("Fetch result:", result)

    # Now navigate to admin panel
    page.goto("http://localhost:8000/attendance/admin-panel/", wait_until="networkidle", timeout=15000)
    print("Admin URL:", page.url)
    print("Admin title:", page.title()[:60])

    cookies = ctx.cookies()
    for c in cookies:
        print("Cookie:", c["name"])

    browser.close()
