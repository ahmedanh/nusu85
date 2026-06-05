import sys
import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8000/attendance/login/", wait_until="networkidle", timeout=15000)
    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "admin123")
    page.click('button[type="submit"]')
    time.sleep(3)
    print("After login URL:", page.url)
    print("Title:", page.title())
    # check cookies
    cookies = page.context.cookies()
    for c in cookies:
        print("Cookie:", c["name"], "=", c["value"][:20] if c["value"] else "")
    browser.close()
