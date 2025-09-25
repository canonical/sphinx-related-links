# This file is part of related-links.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free Software
# Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.

"""Define common function for copying static asset files."""

from pathlib import Path

from sphinx.application import Sphinx
from sphinx.util.fileutil import copy_asset_file


def copy_custom_files(app: Sphinx, exc: Exception | None, filename: str) -> None:
    """Copy the specified file from the _static directory to the build directory.

    app (Sphinx): Sphinx application instance

    exc (Exception | None):

    filename (str):
    """
    if not exc and app.builder.format == "html":
        cssfile = Path(__file__).parent / "_static" / filename
        staticfile = app.builder.outdir / "_static" / filename
        copy_asset_file(cssfile, staticfile)


def add_css(app: Sphinx, filename: str) -> None:
    """Add a CSS file to the static directory.

    app (Sphinx):

    filename (str) :
    """

    def shim(app: Sphinx, exc: Exception | None) -> None:
        return copy_custom_files(app, exc, filename)

    app.connect("build-finished", shim)  # type: ignore[reportUnknownMemberType]
    app.add_css_file(filename)


def add_js(app: Sphinx, filename: str) -> None:
    """Add a javascript file to the static directory.

    app (Sphinx):

    filename (str) :
    """

    def shim(app: Sphinx, exc: Exception | None) -> None:
        return copy_custom_files(app, exc, filename)

    app.connect("build-finished", shim)  # type: ignore[reportUnknownMemberType]
    app.add_js_file(filename)
