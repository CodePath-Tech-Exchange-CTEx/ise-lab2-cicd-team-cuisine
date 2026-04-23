import os
import urllib.error
import urllib.request
from urllib.parse import urlparse

import pytest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _read_project_file(relative_path):
    path = os.path.join(REPO_ROOT, *relative_path)
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def test_dockerfile_includes_streamlit_entrypoint():
    text = _read_project_file(["Dockerfile"])
    assert "EXPOSE 8080" in text
    assert 'ENTRYPOINT ["streamlit", "run", "home.py"]' in text


def test_run_streamlit_script_references_docker_run():
    text = _read_project_file(["run-streamlit.sh"])
    assert "docker build -t streamlit-app ." in text
    assert "docker run -p 8080:8080 streamlit-app" in text


def test_cloud_run_workflow_references_deploy_steps():
    text = _read_project_file([".github", "workflows", "cloud-run.yml"])
    assert "docker/build-push-action@v5" in text
    assert "google-github-actions/deploy-cloudrun@v2" in text


@pytest.mark.skipif(os.environ.get("LIVE_URL") is None, reason="LIVE_URL not set")
def test_live_url_loads_successfully():
    live_url = os.environ["LIVE_URL"]
    parsed = urlparse(live_url)
    assert parsed.scheme in {"http", "https"}, "LIVE_URL must use http or https"
    request = urllib.request.Request(live_url, headers={"User-Agent": "pytest-live-smoke-test"})

    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            assert response.status == 200
            body = response.read(32768).decode("utf-8", errors="replace")
    except urllib.error.URLError as exc:
        pytest.fail(f"Could not fetch LIVE_URL={live_url}: {exc}")

    assert "AirBets" in body or "Welcome to Airbets" in body
