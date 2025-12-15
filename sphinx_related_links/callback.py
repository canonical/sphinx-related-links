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

"""Define the core callback function of related links."""

import json
from collections.abc import Callable
from typing import cast

import requests
from bs4 import BeautifulSoup
from docutils import nodes
from sphinx.application import Sphinx
from sphinx.util import logging

cache: dict[str, str] = {}
logger = logging.getLogger(__name__)


def log_warning(pagename: str, err: str, title: str) -> None:
    """Log a warning for a given page."""
    msg = f"{pagename}: {err}"
    if title:
        msg += f"\nUsing backup link text instead: {title}"
    logger.warning(msg, type="canonical-sphinx-extensions", subtype="linktext")


def get_title(
    post: str, identifier: str, url: str | None, pagename: str
) -> tuple[str, str]:
    """Determine the link title and modify the ID."""
    title = ""

    if post in cache:
        title = cache[post]
    elif identifier.startswith("[") and identifier.endswith(")"):
        split = identifier.partition("](")
        title = split[0][1:]
        identifier = split[2][:-1]
    else:
        if identifier.startswith("{") and identifier.endswith(")"):
            split = identifier.partition("}(")
            # if a backup link text exist, fall back on it if no
            # other title can be retrieved
            title = split[0][1:]
            identifier = split[2][:-1]

        try:
            if url:
                r = requests.get(f"{url}{identifier}.json", timeout=10)
                r.raise_for_status()
                title = json.loads(r.text)["title"]
                cache[post] = title
            else:
                r = requests.get(post, timeout=10)
                r.raise_for_status()
                soup = BeautifulSoup(r.text, "html.parser")
                if soup.title is None:
                    log_warning(pagename, post + " doesn't have a title.", title)
                else:
                    title = soup.title.get_text()
                cache[post] = title
        except requests.HTTPError as err:
            log_warning(pagename, str(err), title)
        except requests.ConnectionError as err:
            log_warning(pagename, str(err), title)

    return title, identifier


def add_context_links(
    app: Sphinx,  # noqa: ARG001
    pagename: str,
    templatename: str,  # noqa: ARG001
    context: dict[str, str | dict[str, str] | Callable[[str], str]],
    doctree: nodes.document,  # noqa: ARG001
) -> None:
    """Add custom elements to Sphinx's context dictionary when the `html-page-context` event is emitted."""

    def discourse_links(id_values: str) -> str:
        if context["discourse_prefix"] and id_values:
            posts = id_values.strip().replace(" ", "").split(",")

            html_links = "<ul>"

            for post in posts:
                title = ""
                post_id = post

                # determine the url (which Discourse to link to)
                # and strip this information from the post_id
                if isinstance(context["discourse_prefix"], dict):
                    id_list = post.split(":")
                    if len(id_list) == 1:
                        url = list(
                            cast(dict[str, str], context["discourse_prefix"]).values()  # type: ignore[redundant-cast]
                        )[0]
                    elif id_list[0] in context["discourse_prefix"]:
                        url = cast(dict[str, str], context["discourse_prefix"])[  # type: ignore[redundant-cast]
                            id_list[0]
                        ]
                        post_id = id_list[1]
                    else:
                        logger.warning(
                            f"{pagename}: Discourse prefix {id_list[0]} is not defined."
                        )
                        continue
                else:
                    url = str(context["discourse_prefix"])

                # determine the title (and maybe strip it from the post_id)
                title, post_id = get_title(post, post_id, url, pagename)

                html_links += (
                    f'<li><a href="{url}{post_id}" target="_blank">{title}</a></li>'
                    if title
                    else ""
                )

            html_links += "</ul>"

            return html_links

        return ""

    def related_links(links: str) -> str:
        if links:
            html_links = links.strip().replace(" ", "").split(",")

            linklist = "<ul>"

            for link in html_links:
                html_link = link
                title = ""

                # determine the title (and maybe strip it from the post_id)
                title, html_link = get_title(html_link, html_link, None, pagename)

                linklist += (
                    (f'<li><a href="{html_link}" target="_blank">{title}</a></li>')
                    if title
                    else ""
                )

            linklist += "</ul>"

            return linklist

        return ""

    context["discourse_links"] = discourse_links
    context["related_links"] = related_links
