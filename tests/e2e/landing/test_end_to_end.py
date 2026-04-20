import os
import urllib.request

BASE_URL = os.environ.get("E2E_BASE_URL", "http://localhost:8080")


def test_app_homepage_is_available():
    """Basic smoke test: app should return HTML on the homepage."""
    request = urllib.request.Request(BASE_URL, headers={"User-Agent": "pytest"})
    with urllib.request.urlopen(request, timeout=10) as response:
        assert response.status == 200
        html = response.read().decode("utf-8", errors="ignore")
        assert "Streamlit" in html or "html" in html.lower()
