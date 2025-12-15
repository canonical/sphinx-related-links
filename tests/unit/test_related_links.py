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

"""Unit tests for related-links extension."""

# Ignore import organization warnings
# ruff: noqa: E402

from unittest.mock import MagicMock, Mock, patch

import pytest
from sphinx.application import Sphinx
from sphinx_related_links import setup


class TestRelatedLinksSetup:
    """Test the extension setup function."""

    def test_setup_returns_metadata(self):
        """Test that setup returns proper extension metadata."""
        app_mock = Mock(spec=Sphinx)
        app_mock.connect = Mock()

        with patch("sphinx_related_links.common.add_css") as mock_add_css:
            result = setup(app_mock)

        assert result.get("parallel_read_safe", "") is True
        assert result.get("parallel_write_safe", "") is True

        # Verify the extension connects to the right event
        app_mock.connect.assert_called_once_with(
            "html-page-context", sphinx_related_links.add_context_links
        )

        # Verify CSS is added
        mock_add_css.assert_called_once_with(app_mock, "related-links.css")


class TestContextFunctions:
    """Test the context functions added by the extension."""

    def setup_method(self):
        """Set up test fixtures."""
        self.app_mock = Mock(spec=Sphinx)
        self.pagename = "test_page"
        self.templatename = "page.html"
        self.context = {}
        self.doctree = Mock()

    def test_discourse_links_no_prefix(self):
        """Test discourse_links when no prefix is configured."""
        self.context["discourse_prefix"] = None

        # Call setup_func to add functions to context
        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        result = self.context["discourse_links"]("12033,13128")
        assert result == ""

    def test_discourse_links_empty_list(self):
        """Test discourse_links with empty ID list."""
        self.context["discourse_prefix"] = "https://discuss.example.com/t/"

        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        result = self.context["discourse_links"]("")
        assert result == ""

    @patch("sphinx_related_links.callback.requests.get")
    def test_discourse_links_with_single_prefix(self, mock_get):
        """Test discourse_links with single prefix configuration."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"title": "Test Topic"}'
        mock_get.return_value = mock_response

        self.context["discourse_prefix"] = "https://discuss.example.com/t/"

        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        result = self.context["discourse_links"]("12033")

        assert "<ul>" in result
        assert "Test Topic" in result
        assert "https://discuss.example.com/t/12033" in result
        assert "</ul>" in result

        mock_get.assert_called_once_with(
            "https://discuss.example.com/t/12033.json", timeout=10
        )

    def test_related_links_empty_list(self):
        """Test related_links with empty link list."""
        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        result = self.context["related_links"]("")
        assert result == ""

    @patch("sphinx_related_links.callback.requests.get")
    @patch("sphinx_related_links.callback.BeautifulSoup")
    def test_related_links_with_urls(self, mock_bs, mock_get):
        """Test related_links with actual URLs."""
        # Mock successful HTTP response
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = "<html><head><title>Example Page</title></head></html>"
        mock_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = Mock()
        mock_soup.title.get_text.return_value = "Example Page"
        mock_bs.return_value = mock_soup

        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        result = self.context["related_links"]("https://example.com")

        assert "<ul>" in result
        assert "Example Page" in result
        assert "https://example.com" in result
        assert "</ul>" in result

        mock_get.assert_called_once_with("https://example.com", timeout=10)

    @patch("sphinx_related_links.callback.cache", {})
    @patch("sphinx_related_links.callback.requests.get")
    def test_discourse_links_with_dict_prefix_default_server(self, mock_get):
        """Test that dict prefix handles default server without exception."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"title": "Test Topic"}'
        mock_get.return_value = mock_response

        self.context["discourse_prefix"] = {
            "server1": "https://server1.example.com/t/",
            "server2": "https://server2.example.com/t/",
        }

        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        # Should not raise TypeError when accessing dict.values()[0]
        result = self.context["discourse_links"]("11111")
        assert result  # Just verify something was returned

    @patch("sphinx_related_links.callback.cache", {})
    @patch("sphinx_related_links.callback.requests.get")
    def test_discourse_links_with_dict_prefix_specific_server(self, mock_get):
        """Test that dict prefix handles specific server without exception."""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.text = '{"title": "Test Topic"}'
        mock_get.return_value = mock_response

        self.context["discourse_prefix"] = {
            "server1": "https://server1.example.com/t/",
            "server2": "https://server2.example.com/t/",
        }

        sphinx_related_links.add_context_links(
            self.app_mock, self.pagename, self.templatename, self.context, self.doctree
        )

        # Should handle server-specific format
        result = self.context["discourse_links"]("server2:22222")
        assert result  # Just verify something was returned


# Import the module after defining the tests
import sphinx_related_links
