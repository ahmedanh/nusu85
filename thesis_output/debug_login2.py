import time
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 900})
    page.goto("http://localhost:8000/attendance/login/", wait_until="networkidle", timeout=15000)
    # Check what the submit button looks like
    buttons = page.query_selector_all("button")
    for b in buttons:
        print("button type:", b.get_attribute("type"), "text:", b.inner_text()[:40])
    # Try form action
    form = page.query_selector("form")
    if form:
        print("form action:", form.get_attribute("action"))
        print("form method:", form.get_attribute("method"))

    page.fill('input[name="username"]', "admin")
    page.fill('input[name="password"]', "admin123")

    # watch network
    responses = []
    page.on("response", lambda r: responses.append((r.status, r.url)))

    page.click('button[type="submit"]')
    time.sleep(2)
    print("After submit URL:", page.url)
    for s, u in responses:
        print(f"  {s} {u}")
    browser.close()
