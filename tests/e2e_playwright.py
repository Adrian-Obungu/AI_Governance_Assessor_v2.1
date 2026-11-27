import json
import hashlib
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

BASE_URL = os.environ.get("BASE_URL", "http://localhost/").rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "test-artifacts" / "playwright"
DOWNLOADS = EVIDENCE / "downloads"
EVIDENCE.mkdir(parents=True, exist_ok=True)
DOWNLOADS.mkdir(parents=True, exist_ok=True)

stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")
email = f"browser-{stamp}@example.com"
password = "BrowserJourney123!"
title = f"Browser evidence assessment {stamp}"

console_messages = []
page_errors = []
network_failures = []
http_errors = []
steps = []

def sha256(path: Path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def screenshot(page, name):
    path = EVIDENCE / f"{name}.png"
    page.screenshot(path=str(path), full_page=True)
    return str(path.relative_to(ROOT))

def record(step, page, extra=None):
    item = {"step": step, "url": page.url, "screenshot": screenshot(page, step)}
    if extra:
        item.update(extra)
    steps.append(item)

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True, executable_path="/usr/bin/chromium", args=["--no-sandbox"])
    context = browser.new_context(accept_downloads=True, viewport={"width": 1440, "height": 1000})
    context.tracing.start(screenshots=True, snapshots=True, sources=True)
    page = context.new_page()
    page.on("console", lambda msg: console_messages.append({"type": msg.type, "text": msg.text}))
    page.on("pageerror", lambda exc: page_errors.append(str(exc)))
    page.on("requestfailed", lambda req: network_failures.append({"url": req.url, "method": req.method, "failure": req.failure}))
    page.on("response", lambda res: http_errors.append({"url": res.url, "status": res.status}) if res.status >= 400 else None)

    # Login page and account creation; signup immediately establishes a logged-in session.
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    expect(page.get_by_role("heading", name="AI Governance Assessor")).to_be_visible()
    record("01-login-page", page, {"email": email})
    page.get_by_role("button", name="Don't have an account? Sign up").click()
    page.get_by_label("Full name").fill("Browser Evidence User")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Create account").click()
    expect(page).to_have_url(re.compile(r"/dashboard$"))
    expect(page.get_by_role("button", name="Logout")).to_be_visible()
    record("02-account-created-and-logged-in", page)

    # Explicit login verification: logout, then sign back in through the login form.
    page.get_by_role("button", name="Logout").click()
    expect(page).to_have_url(re.compile(r"/dashboard$|/login$"))
    page.goto(f"{BASE_URL}/login", wait_until="networkidle")
    page.get_by_label("Email").fill(email)
    page.get_by_label("Password").fill(password)
    page.get_by_role("button", name="Sign in").click()
    expect(page).to_have_url(re.compile(r"/dashboard$"))
    record("03-login-success", page)

    # Create a new assessment from the dashboard modal.
    page.get_by_role("button", name=re.compile(r"New Assessment|Start first assessment")).first.click()
    expect(page.get_by_role("dialog")).to_be_visible()
    page.get_by_label("Title").fill(title)
    page.get_by_label("Description (optional)").fill("Browser-level evidence for the complete assessment journey.")
    page.get_by_role("dialog").get_by_role("button", name="Create").click()
    expect(page.get_by_text(title, exact=True)).to_be_visible()
    record("04-assessment-created", page)
    page.get_by_text(title, exact=True).click()
    expect(page).to_have_url(re.compile(r"/assessment/\d+$"))
    expect(page.get_by_role("progressbar")).to_be_visible()
    record("05-assessment-opened", page)

    # Complete every live questionnaire category using the highest available option per question.
    category_results = []
    category_buttons = page.locator("button[aria-current]")
    # Start with the currently selected category, then follow the category list by title.
    for index in range(4):
        heading = page.locator("h2").filter(has_text="").last
        # Select all currently visible radio choices, one per question, taking the last option.
        fieldsets = page.locator("fieldset")
        question_count = fieldsets.count()
        assert question_count > 0, f"No questions rendered for category index {index}"
        for q in range(question_count):
            fieldsets.nth(q).locator("input[type=radio]").last.check()
        current_title = page.locator("h2").last.inner_text()
        button_name = "Complete assessment" if index == 3 else "Save and continue"
        page.get_by_role("button", name=button_name).click()
        if index < 3:
            expect(page.get_by_role("status")).to_contain_text("Section saved")
            record(f"06-category-{index+1}-completed", page, {"category_title": current_title, "questions": question_count})
        else:
            # The implementation may leave the completed assessment on the assessment
            # page with a View Report action rather than auto-navigating.
            if not re.search(r"/report/\d+$", page.url):
                expect(page.get_by_text(re.compile(r"4 of 4 sections complete"))).to_be_visible()
                report_button = page.get_by_role("button", name="View Report")
                if report_button.count():
                    report_button.click()
                else:
                    assessment_id = re.search(r"/assessment/(\d+)$", page.url).group(1)
                    page.goto(f"{BASE_URL}/report/{assessment_id}", wait_until="networkidle")
            expect(page).to_have_url(re.compile(r"/report/\d+$"))
            category_results.append({"category_title": current_title, "questions": question_count})
    record("10-all-categories-completed-report-generated", page, {"categories": category_results})
    expect(page.get_by_text("Assessment Report", exact=True)).to_be_visible()
    expect(page.get_by_text(re.compile(r"Maturity$"))).to_be_visible()

    # Validate both browser-triggered file downloads and retain deterministic hashes.
    download_evidence = []
    for fmt in ("csv", "pdf"):
        with page.expect_download(timeout=15000) as download_info:
            page.get_by_role("button", name=f"Export {fmt.upper()}").click()
        download = download_info.value
        target = DOWNLOADS / f"assessment.{fmt}"
        download.save_as(str(target))
        assert target.exists() and target.stat().st_size > 0
        download_evidence.append({"format": fmt, "filename": download.suggested_filename, "path": str(target.relative_to(ROOT)), "bytes": target.stat().st_size, "sha256": sha256(target)})
        record(f"11-export-{fmt}", page, {"download": download_evidence[-1]})

    # Logout and prove protected navigation returns to login.
    page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
    expect(page.get_by_role("button", name="Logout")).to_be_visible()
    page.get_by_role("button", name="Logout").click()
    page.goto(f"{BASE_URL}/dashboard", wait_until="networkidle")
    expect(page).to_have_url(re.compile(r"/login$"))
    expect(page.get_by_role("heading", name="AI Governance Assessor")).to_be_visible()
    record("12-logout-and-protected-route", page)

    context.tracing.stop(path=str(EVIDENCE / "playwright-trace.zip"))
    context.close()
    browser.close()

summary = {
    "base_url": BASE_URL,
    "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    "account": {"email": email, "password": password, "synthetic": True},
    "steps": steps,
    "downloads": download_evidence,
    "console_messages": console_messages,
    "page_errors": page_errors,
    "network_failures": network_failures,
    "http_errors": http_errors,
    "trace": "test-artifacts/playwright/playwright-trace.zip",
}
(EVIDENCE / "evidence.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps({"status": "passed", "steps": len(steps), "downloads": download_evidence, "page_errors": page_errors, "network_failures": network_failures, "http_errors": http_errors}, indent=2))
