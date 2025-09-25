# This file is part of sphinx-ext-template.
#
# Copyright 2025 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License version 3, as published by the Free
# Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranties of MERCHANTABILITY, SATISFACTORY
# QUALITY, or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public
# License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.

"""Contains the extension's directive."""

from docutils import nodes
from sphinx.util.docutils import SphinxDirective


class HelloDirective(SphinxDirective):
    """A directive to say hello."""

    required_arguments = 1

    def run(self) -> list[nodes.Node]:
        """Write a greeting.

        :returns: list[nodes.Node]
        """
        paragraph_node = nodes.paragraph(text=f"Hello, {self.arguments[0]}!")
        return [paragraph_node]
