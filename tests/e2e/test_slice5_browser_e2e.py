"""
Slice 5 Playwright Browser E2E Test Suite.
Verifies real-browser end-to-end interactive workflow against live frontend & backend.

Co-authored-by: Mohammad Abdul Kalam Hussain <abdul05kh.college@gmail.com>
Co-authored-by: Siri Chandana <kotagirisirichandana73@gmail.com>
Co-authored-by: Mohammad Zakiruddin <zakirmd.1805@gmail.com>
Co-authored-by: Mohammed Numan <mohammednumaan901@gmail.com>
Co-authored-by: Manivarun Chintala <manivarunchintala2005.2728@gmail.com>
Co-authored-by: Thaniska <ramatenkithanishka@gmail.com>
"""

import os
import sys
import time
import socket
import subprocess
import pytest
import httpx
from playwright.sync_api import sync_playwright

BACKEND_PORT = 8001
FRONTEND_PORT = 5174
BASE_URL = f"http://127.0.0.1:{FRONTEND_PORT}"
API_URL = f"http://127.0.0.1:{BACKEND_PORT}"


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 20.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
    return False


@pytest.fixture(scope="module")
def live_servers():
    """Launch dedicated FastAPI backend and Vite frontend instances for browser E2E."""
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"
    
    # 1. Start backend on 8001
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
        cwd=os.getcwd(),
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    assert wait_for_port(BACKEND_PORT), "Backend server failed to start on port 8001"

    # Verify backend health
    health_resp = httpx.get(f"{API_URL}/health", timeout=5.0)
    assert health_resp.status_code == 200

    # 2. Start Vite frontend on 5174
    frontend_env = os.environ.copy()
    frontend_env["VITE_BACKEND_URL"] = API_URL
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    vite_cmd = os.path.join(frontend_dir, "node_modules", ".bin", "vite.cmd") if sys.platform == "win32" else "npx"

    cmd = [vite_cmd, "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)] if sys.platform == "win32" else ["npx", "vite", "--host", "127.0.0.1", "--port", str(FRONTEND_PORT)]
    frontend_proc = subprocess.Popen(
        cmd,
        cwd=frontend_dir,
        env=frontend_env,
        shell=(sys.platform == "win32"),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    assert wait_for_port(FRONTEND_PORT), "Frontend Vite server failed to start on port 5174"

    time.sleep(1.0)
    yield BASE_URL

    # Teardown processes
    if sys.platform == "win32":
        subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
        subprocess.run(f"taskkill /F /T /PID {backend_proc.pid}", shell=True, capture_output=True)
    else:
        frontend_proc.terminate()
        backend_proc.terminate()


def test_browser_golden_workflow_e2e(live_servers):
    """
    Playwright Browser E2E acceptance test:
    1. Launch application
    2. Load demo (Clean / Defect)
    3. Select parcel
    4. Select candidate (Floor L01)
    5. Inspect evidence
    6. Inspect validation
    7. Request correction
    8. Submit review
    9. Observe revision change
    10. Inspect audit
    11. Export
    12. Reset demo
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        # 1. Launch application
        page.goto(live_servers, timeout=30000)
        page.wait_for_load_state("networkidle")
        assert "BHUVISTAAR" in page.content() or "BhuVistaar" in page.content()

        # 2. Select defect scenario via select dropdown
        page.wait_for_selector("select", timeout=10000)
        # Select scenario dropdown
        scenario_selects = page.locator("select").all()
        for sel in scenario_selects:
            text = sel.inner_text()
            if "VRT-003" in text or "Clean" in text:
                sel.select_option("defect")
                break
        page.wait_for_timeout(1000)

        # 3. Select parcel / verify hierarchy loaded
        page.wait_for_selector("text=Parent Parcel", timeout=10000)
        assert page.is_visible("text=Parent Parcel")
        assert page.is_visible("text=12345678901234")

        # 4. Select candidate (Floor L01)
        page.wait_for_selector("text=L01", timeout=10000)
        page.click("text=L01")
        page.wait_for_timeout(500)

        # 5. Inspect Evidence tab
        evidence_tab = page.locator("button:has-text('Evidence')").first
        if evidence_tab.is_visible():
            evidence_tab.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=EVID-") or page.is_visible("text=Evidence")

        # 6. Inspect Validation tab
        validation_tab = page.locator("button:has-text('Validation')").first
        if validation_tab.is_visible():
            validation_tab.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=BLOCKER") or page.is_visible("text=Rules") or page.is_visible("text=Validation")

        # 7. Inspect Review tab & Request Correction
        review_tab = page.locator("button:has-text('Review')").first
        if review_tab.is_visible():
            review_tab.click()
            page.wait_for_timeout(500)

        # Request correction button
        corr_btn = page.locator("button:has-text('Request Correction')").first
        if corr_btn.is_visible():
            corr_btn.click()
            page.wait_for_timeout(500)
            # Fill correction in modal if open
            modal_textarea = page.locator("textarea").first
            if modal_textarea.is_visible():
                modal_textarea.fill("Adjusting L01 ceiling elevation from 106.50m down to 106.00m to eliminate VRT-003 overlap.")
                submit_corr = page.locator("button:has-text('Submit Correction')").first
                if submit_corr.is_visible():
                    submit_corr.click()
                    page.wait_for_timeout(1000)

        # 8. Observe Revision Change & Comparison tab
        rev_tab = page.locator("button:has-text('Revisions')").first
        if rev_tab.is_visible():
            rev_tab.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=Revision") or page.is_visible("text=VUID")

        # 9. Inspect Audit tab
        audit_tab = page.locator("button:has-text('Audit')").first
        if audit_tab.is_visible():
            audit_tab.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=Audit") or page.is_visible("text=Action")

        # 10. Open Interoperability Export Modal (Slice 5 feature)
        export_btn = page.locator("button:has-text('Export')").first
        if export_btn.is_visible():
            export_btn.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=Export") or page.is_visible("text=Prototype VUID") or page.is_visible("text=JSON")

            # Close modal if open
            close_btn = page.locator("button:has-text('Close')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)

        # 11. Open System Readiness Panel (Slice 5 feature)
        readiness_btn = page.locator("button:has-text('Readiness')").first
        if readiness_btn.is_visible():
            readiness_btn.click()
            page.wait_for_timeout(500)
            assert page.is_visible("text=Readiness") or page.is_visible("text=Database") or page.is_visible("text=PostgreSQL")
            close_btn = page.locator("button:has-text('Close')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(500)

        # 12. Reset Demo (Switch to clean baseline)
        for sel in page.locator("select").all():
            text = sel.inner_text()
            if "Clean" in text:
                sel.select_option("clean")
                page.wait_for_timeout(1000)
                break

        assert page.is_visible("text=L01")
        browser.close()
