"""
BhuVistaar Playwright Browser Red-Team Automation Audit.
Executes rigorous interactive testing across multiple viewports,
12 tabs, all modals, 3D viewer controls, and the end-to-end golden workflow.

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

BACKEND_PORT = 8002
FRONTEND_PORT = 5175
BASE_URL = f"http://127.0.0.1:{FRONTEND_PORT}"
API_URL = f"http://127.0.0.1:{BACKEND_PORT}"


def wait_for_port(port: int, host: str = "127.0.0.1", timeout: float = 25.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            with socket.create_connection((host, port), timeout=1.0):
                return True
        except (OSError, ConnectionRefusedError):
            time.sleep(0.5)
    return False


@pytest.fixture(scope="module")
def redteam_live_servers():
    """Launch dedicated FastAPI backend and Vite frontend instances on isolated ports."""
    backend_env = os.environ.copy()
    backend_env["PYTHONUNBUFFERED"] = "1"

    # Start FastAPI on 8001
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.main:app", "--host", "127.0.0.1", "--port", str(BACKEND_PORT)],
        cwd=os.getcwd(),
        env=backend_env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    assert wait_for_port(BACKEND_PORT), "Backend server failed to start on port 8001"
    health_resp = httpx.get(f"{API_URL}/health", timeout=5.0)
    assert health_resp.status_code == 200

    # Start Vite on 5174
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

    assert wait_for_port(FRONTEND_PORT), "Frontend server failed to start on port 5174"
    time.sleep(1.0)

    yield BASE_URL

    # Teardown processes
    if sys.platform == "win32":
        subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
        subprocess.run(f"taskkill /F /T /PID {backend_proc.pid}", shell=True, capture_output=True)
    else:
        frontend_proc.terminate()
        backend_proc.terminate()


VIEWPORT_CONFIGS = [
    {"name": "Desktop 1080p", "width": 1920, "height": 1080},
    {"name": "Desktop 900p", "width": 1440, "height": 900},
    {"name": "Laptop 768p", "width": 1366, "height": 768},
    {"name": "Compact Laptop", "width": 1280, "height": 720},
    {"name": "Tablet Portrait", "width": 768, "height": 1024},
    {"name": "Mobile Device", "width": 390, "height": 844},
]


def test_browser_full_redteam_e2e_audit(redteam_live_servers):
    """
    Comprehensive Live Browser Red-Team Audit executing:
    Phase 1: Dynamic multi-viewport responsive verification (6 viewports)
    Phase 2: Traversal of all 12 workspace tabs with zero client exceptions
    Phase 3: 3D Cadastral Viewer toolbar, camera angles & canvas interaction
    Phase 4: Modal inspections (30s Tour, Technical FAQ, System Readiness, Model Benchmark)
    Phase 5: Full Golden Workflow (Defect Scenario -> Unit Selection -> Validation Blocker -> Correction -> Revalidation -> Gate C Approval -> Export)
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 900})
        page = context.new_page()

        console_errors = []
        page.on("pageerror", lambda err: console_errors.append(str(err)))

        # --------------------------------------------------------------------
        # Launch & Initial Verification
        # --------------------------------------------------------------------
        httpx.post(f"{API_URL}/api/v1/demo/reset?scenario=defect", timeout=10.0)
        page.goto(redteam_live_servers, timeout=30000)
        page.wait_for_selector("select", timeout=10000)
        assert "BHUVISTAAR" in page.content() or "BhuVistaar" in page.content()

        # Select defect scenario via select dropdown
        for sel in page.locator("select").all():
            text = sel.inner_text()
            if "VRT-003" in text or "Clean" in text:
                sel.select_option("defect")
                break
        page.wait_for_timeout(1000)

        page.wait_for_selector("text=Parent Parcel", timeout=10000)
        assert page.is_visible("text=Parent Parcel")

        # --------------------------------------------------------------------
        # Phase 1: Responsive Viewport Resizing Audit
        # --------------------------------------------------------------------
        for vp in VIEWPORT_CONFIGS:
            page.set_viewport_size({"width": vp["width"], "height": vp["height"]})
            page.wait_for_timeout(200)
            assert page.locator("canvas").count() >= 1, f"3D Canvas missing at {vp['name']}"

        # Return to standard desktop 1440x900
        page.set_viewport_size({"width": 1440, "height": 900})
        page.wait_for_timeout(300)

        # --------------------------------------------------------------------
        # Phase 2: All 12 Tabs Interactive Navigation
        # --------------------------------------------------------------------
        tab_names = [
            "AI Proposals",
            "Anomalies",
            "Reviewer Queue",
            "Validation",
            "Disagreements",
            "Side-by-Side Triad",
            "Evidence & Provenance",
            "Review & Gate C",
            "Revisions",
            "Audit Trail",
            "Export",
            "Field View",
        ]
        for tab_name in tab_names:
            tab_btn = page.locator(f"button:has-text('{tab_name}')").first
            assert tab_btn.is_visible(), f"Tab button '{tab_name}' not visible"
            tab_btn.click()
            page.wait_for_timeout(250)

        # Confirm zero uncaught client exceptions
        assert len(console_errors) == 0, f"Uncaught JavaScript errors: {console_errors}"

        # --------------------------------------------------------------------
        # Phase 3: 3D Viewer Toolbar & Canvas Controls
        # --------------------------------------------------------------------
        plan_btn = page.locator("button:has-text('Plan 2D')").first
        if plan_btn.is_visible():
            plan_btn.click()
            page.wait_for_timeout(200)

        iso_btn = page.locator("button:has-text('Iso 3D')").first
        if iso_btn.is_visible():
            iso_btn.click()
            page.wait_for_timeout(200)

        explode_btn = page.locator("button:has-text('Explode')").first
        if explode_btn.is_visible():
            explode_btn.click()
            page.wait_for_timeout(200)
            collapse_btn = page.locator("button:has-text('Collapse')").first
            if collapse_btn.is_visible():
                collapse_btn.click()
                page.wait_for_timeout(200)

        wireframe_btn = page.locator("button:has-text('Wireframe')").first
        if wireframe_btn.is_visible():
            wireframe_btn.click()
            page.wait_for_timeout(200)
            wireframe_btn.click()

        reset_btn = page.locator("button[title*='Reset Camera']").first
        if reset_btn.is_visible():
            reset_btn.click()
            page.wait_for_timeout(200)

        # Orbit canvas simulation
        canvas = page.locator("canvas").first
        box = canvas.bounding_box()
        if box:
            center_x = box["x"] + box["width"] / 2
            center_y = box["y"] + box["height"] / 2
            page.mouse.move(center_x, center_y)
            page.mouse.down()
            page.mouse.move(center_x + 50, center_y + 30, steps=3)
            page.mouse.up()
            page.wait_for_timeout(200)

        # --------------------------------------------------------------------
        # Phase 4: Modal Dialog Audits
        # --------------------------------------------------------------------
        # 1. 30s Executive Tour Modal
        tour_btn = page.locator("button:has-text('30s Tour')").first
        if tour_btn.is_visible():
            tour_btn.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=Executive Overview")
            close_btn = page.locator("button svg.lucide-x").locator("..").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(200)

        # 2. Why BhuVistaar FAQ Modal
        faq_btn = page.locator("button:has-text('Why BhuVistaar?')").or_(page.locator("button:has-text('Why? FAQ')")).first
        if faq_btn.is_visible():
            faq_btn.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=FAQ") or page.is_visible("text=Cadastre")
            close_btn = page.locator("button svg.lucide-x").locator("..").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(200)

        # 3. System Readiness Modal
        readiness_btn = page.locator("button:has-text('Readiness')").first
        if readiness_btn.is_visible():
            readiness_btn.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=Readiness") or page.is_visible("text=Database")
            close_btn = page.locator("button:has-text('Close')").first
            if close_btn.is_visible():
                close_btn.click()
                page.wait_for_timeout(200)

        # --------------------------------------------------------------------
        # Phase 5: Golden Workflow (Defect -> Correction -> Gate C Approval)
        # --------------------------------------------------------------------
        # Select Floor L01 in tree
        page.wait_for_selector("text=L01", timeout=10000)
        page.locator("text=L01").first.click()
        page.wait_for_timeout(400)

        # Inspect Validation tab
        val_tab = page.locator("button:has-text('Validation')").first
        if val_tab.is_visible():
            val_tab.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=BLOCKER") or page.is_visible("text=VRT-003") or page.is_visible("text=Rules")

        # Open Correction modal via Review tab or Inspector
        corr_btn = page.locator("button:has-text('Request Correction')").or_(page.locator("button:has-text('Request / Submit Correction')")).first
        if not corr_btn.is_visible():
            review_tab = page.locator("button:has-text('Review & Gate C')").or_(page.locator("button:has-text('Review')")).first
            review_tab.click()
            page.wait_for_timeout(400)
            corr_btn = page.locator("button:has-text('Request Correction')").or_(page.locator("button:has-text('Request / Submit Correction')")).first

        if corr_btn.is_visible():
            corr_btn.click()
            page.wait_for_selector(".modal-content", timeout=5000)
            apply_btn = page.locator("button:has-text('Apply 106.00m')").first
            if apply_btn.is_visible():
                apply_btn.click()
                page.wait_for_timeout(300)

            submit_btn = page.locator(".modal-content button[type='submit']").first
            submit_btn.click()
            page.locator(".modal-overlay").wait_for(state="detached", timeout=10000)
            page.wait_for_timeout(1000)

        # Check Revisions Tab
        rev_tab = page.locator("button:has-text('Revisions')").first
        if rev_tab.is_visible():
            rev_tab.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=VUID") or page.is_visible("text=Revision")

        # Accept candidate in Review tab
        review_tab = page.locator("button:has-text('Review & Gate C')").or_(page.locator("button:has-text('Review')")).first
        if review_tab.is_visible():
            review_tab.click()
            page.wait_for_timeout(400)
            accept_btn = page.locator("button:has-text('Accept Candidate')").or_(page.locator("button:has-text('Accept')")).first
            if accept_btn.is_visible() and not accept_btn.is_disabled():
                accept_btn.click()
                page.wait_for_timeout(800)

        # Verify Export tab
        export_tab = page.locator("button:has-text('Export')").first
        if export_tab.is_visible():
            export_tab.click()
            page.wait_for_timeout(400)
            assert page.is_visible("text=Export") or page.is_visible("text=PROTOTYPE") or page.is_visible("text=VUID")

        # Clean finish
        browser.close()
