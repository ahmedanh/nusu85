# -*- coding: utf-8 -*-
import sys
import time
import requests
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding="utf-8")

BASE = "http://localhost:8000"

def get_session_cookie(username, password):
    """Use requests to get a real Django session cookie."""
    s = requests.Session()
    # Get CSRF
    r = s.get(f"{BASE}/attendance/login/")
    csrf = s.cookies.get("csrftoken")
    print(f"  CSRF: {csrf[:10] if csrf else 'NONE'}")
    # POST login
    r2 = s.post(f"{BASE}/attendance/login/", data={
        "csrfmiddlewaretoken": csrf,
        "username": username,
        "password": password,
    }, headers={"Referer": f"{BASE}/attendance/login/"}, allow_redirects=True)
    print(f"  POST status: {r2.status_code}, final URL: {r2.url}")
    print(f"  Cookies: {list(s.cookies.keys())}")
    return s.cookies.get("sessionid"), csrf, s.cookies.get("csrftoken")

print("Testing admin login...")
sid, csrf_old, csrf_new = get_session_cookie("admin", "admin123")
print(f"  sessionid: {sid[:10] if sid else 'NONE'}")
