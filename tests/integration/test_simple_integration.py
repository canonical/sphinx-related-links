# This file is part of related-links.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU Lesser General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
# License for more details.
#
# You should have received a copy of the GNU Lesser General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Simple integration tests for related-links extension."""

# Ignore import organization warnings
# ruff: noqa: E402
# ruff: noqa: PLC0415

import shutil
import sys
from collections.abc import Callable
from pathlib import Path
from unittest.mock import Mock

import bs4

# Add the extension to the path
sys.path.insert(0, str(Path(__file__).parents[2] / "sphinx_related_links"))


def test_extension_can_be_imported():
    """Test that the extension can be imported without errors."""
    try:
        import sphinx_related_links

        assert hasattr(sphinx_related_links, "setup")
        assert callable(sphinx_related_links.setup)
    except ImportError as e:
        pytest.fail(f"Failed to import sphinx_related_links: {e}")


def test_extension_setup_function():
    """Test that the setup function returns correct metadata."""
    from unittest.mock import Mock

    import sphinx_related_links

    app_mock = Mock()
    app_mock.connect = Mock()

    with patch("sphinx_related_links.common.add_css") as mock_add_css:
        result = sphinx_related_links.setup(app_mock)

    assert "version" in result
    assert "parallel_read_safe" in result
    assert "parallel_write_safe" in result
    assert result["parallel_read_safe"] is True
    assert result["parallel_write_safe"] is True


def test_context_functions_work():
    """Test that context functions can be called."""
    from unittest.mock import Mock

    import sphinx_related_links

    app_mock = Mock()
    pagename = "test"
    templatename = "test.html"
    context: dict[str, str | dict[str, str] | Callable[[str], str]] = {
        "discourse_prefix": ""
    }
    doctree = Mock()

    # Call the setup function
    sphinx_related_links.add_context_links(
        app_mock, pagename, templatename, context, doctree
    )

    # Check that context functions were added
    assert "discourse_links" in context
    assert "related_links" in context
    assert callable(context["discourse_links"])
    assert callable(context["related_links"])

    # Test empty calls
    assert context["discourse_links"]("") == ""
    assert context["related_links"]("") == ""


# Import necessary modules
from unittest.mock import patch

import pytest


@pytest.fixture
def example_project(request) -> Path:
    project_root = request.config.rootpath
    example_dir = project_root / "tests/integration/example"

    # Copy the project into the test's own temporary dir, to avoid clobbering
    # the sources.
    target_dir = Path().resolve() / "example"
    shutil.copytree(example_dir, target_dir, dirs_exist_ok=True)

    return target_dir


# Canned responses for the pages that the example project links to, so that the
# build doesn't depend on discourse.ubuntu.com or ubuntu.com being reachable.
FAKE_RESPONSES = {
    "https://discourse.ubuntu.com/t/57290.json": '{"title": "General posting guidelines"}',
    "https://ubuntu.com/": "<html><head><title>Ubuntu test page</title></head></html>",
}


def fake_get(url: str, timeout: float) -> Mock:
    response = Mock()
    response.raise_for_status.return_value = None
    response.text = FAKE_RESPONSES[url]
    return response


@pytest.mark.slow
def test_sphinx_build(example_project, mocker):
    from sphinx.cmd.build import build_main
    from sphinx_related_links import callback

    # Run Sphinx in this process so that the HTTP requests can be patched.
    mocker.patch.dict(callback.cache, clear=True)
    mock_get = mocker.patch(
        "sphinx_related_links.callback.requests.get", side_effect=fake_get
    )

    build_dir = example_project / "_build"
    exit_code = build_main(["-b", "html", "-W", str(example_project), str(build_dir)])
    assert exit_code == 0

    requested = {call.args[0] for call in mock_get.call_args_list}
    assert requested == set(FAKE_RESPONSES)

    index = build_dir / "index.html"

    # Rename the test output to something more meaningful
    shutil.copytree(
        build_dir, build_dir.parents[1] / ".test_output", dirs_exist_ok=True
    )

    soup = bs4.BeautifulSoup(index.read_text(), features="lxml")
    shutil.rmtree(example_project)  # Delete copied source

    assert soup.find("div", {"class": "relatedlinks-container"})

    discourse_link = soup.find("a", {"href": "https://discourse.ubuntu.com/t/57290"})
    if discourse_link:
        assert discourse_link.get_text() == "General posting guidelines"
    else:
        pytest.fail("Discourse link not found in HTML output.")

    related_link = soup.find("a", {"href": "https://ubuntu.com/"})
    if related_link:
        # Normalize whitespace as the actual HTML may contain formatting whitespace
        import re

        actual_text = re.sub(r"\s+", " ", related_link.get_text().strip())
        assert actual_text == "Ubuntu test page"
    else:
        pytest.fail("Related link not found in HTML output.")
