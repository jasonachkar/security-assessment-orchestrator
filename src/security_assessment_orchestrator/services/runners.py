from __future__ import annotations

import subprocess
from dataclasses import dataclass

import httpx

from security_assessment_orchestrator.infra.settings import Settings


@dataclass(frozen=True)
class ToolResult:
    kind: str
    content_type: str
    content: str


def run_nmap(target: str) -> ToolResult:
    # Discovery + service detection; no exploitation.
    cmd = ["nmap", "-sV", "-O", "-T3", "--reason", target]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    out = proc.stdout + "
" + proc.stderr
    return ToolResult(kind="nmap", content_type="text/plain", content=out.strip())


def run_zap_quick_scan(target_url: str) -> ToolResult:
    # Uses ZAP in daemon mode via JSON API (same container network).
    base = Settings().zap_base_url.rstrip("/")
    # Trigger spider then active scan (basic flow).
    with httpx.Client(timeout=30.0) as client:
        spider = client.get(f"{base}/JSON/spider/action/scan/", params={"url": target_url})
        spider.raise_for_status()
        spider_id = spider.json()["scan"]

        # best-effort wait
        while True:
            st = client.get(f"{base}/JSON/spider/view/status/", params={"scanId": spider_id})
            st.raise_for_status()
            if int(st.json()["status"]) >= 100:
                break

        ascan = client.get(f"{base}/JSON/ascan/action/scan/", params={"url": target_url})
        ascan.raise_for_status()
        ascan_id = ascan.json()["scan"]

        while True:
            st = client.get(f"{base}/JSON/ascan/view/status/", params={"scanId": ascan_id})
            st.raise_for_status()
            if int(st.json()["status"]) >= 100:
                break

        alerts = client.get(f"{base}/JSON/core/view/alerts/", params={"baseurl": target_url})
        alerts.raise_for_status()
        return ToolResult(kind="zap", content_type="application/json", content=alerts.text)


def run_trivy_image(image_ref: str) -> ToolResult:
    # Trivy is not installed by default here; this runner expects you to enable and install in Dockerfile if you want it.
    cmd = ["trivy", "image", "--format", "json", image_ref]
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False)
    out = proc.stdout if proc.stdout else proc.stderr
    return ToolResult(kind="trivy", content_type="application/json", content=out.strip())
