# sphinx-related-links

sphinx-related-links adds functionality to Sphinx that allows adding related links on a
per-page basis, supporting both Discourse topic links and custom related URLs.

## Basic usage

### Adding Discourse links

Configure the Discourse prefix in your `conf.py`:

```python
html_context = {
    "discourse_prefix": "https://discuss.linuxcontainers.org/t/"
}

html_context = {
    "discourse_prefix": {
        "ubuntu": "https://discourse.ubuntu.com/t/",
        "lxc": "https://discuss.linuxcontainers.org/t/"
    }
}
```

Add the desired Discourse topic IDs to the page's metadata. For MyST files, this is done
with [frontmatter](https://mystmd.org/guide/frontmatter).

```
---
discourse: 12033,13128
---
```

For rST sources, metadata content can be added with the following syntax:

```
:discourse: 12033, 13128
```

### Adding custom related links

Add URLs to page metadata:

```
---
relatedlinks: https://www.example.com, https://www.google.com
---
```

## Project setup

sphinx-related-links is published on PyPI and can be installed with:

```bash
pip install sphinx-related-links
```

After adding sphinx-related-links to your Python project, update your Sphinx's conf.py file to
include sphinx-related-links as one of its extensions:

```python
extensions = [
    "sphinx_related_links"
]
```

Lastly, update your [Sphinx project's
templates](https://www.sphinx-doc.org/en/master/development/html_themes/templating.html)
to include the metadata content in the right-hand sidebar. This will depend on your
project's theme. An example template can be seen in this project's [integration
tests](/tests/integration/example/_templates/page.html).

## Community and support

You can report any issues or bugs on the project's [GitHub
repository](https://github.com/canonical/sphinx-related-links).

sphinx-related-links is covered by the [Ubuntu Code of
Conduct](https://ubuntu.com/community/ethos/code-of-conduct).

## License and copyright

sphinx-related-links is released under the [GPL-3.0 license](LICENSE).

© 2025 Canonical Ltd.
