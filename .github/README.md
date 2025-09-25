# Canonical Sphinx extension template

This repository is a template for Canonical's Sphinx extensions. It provides useful
boilerplate and tools for linting, testing, and publishing Sphinx extensions.

## Create an extension

When creating an extension, start by [creating a GitHub repository from this
template](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-repository-from-a-template).

Once the repository has been created, update the top-level README and CONTRIBUTING
templates to better reflect your extension.

Next, replace any references to the placeholder `hello_ext` extension in the following
files:

- `pyproject.toml`
- `Makefile`
- `hello_ext/`
- `tests/unit/`
- `tests/integration/`

Note the difference between the project name, `hello-ext`, and the module name,
`hello_ext`. Due to Python's naming conventions, this pattern must be preserved in the
new extension.

Finally, delete `.github/README.md`, as it will take precedence over your top-level
README if left intact.

## Migrate an extension

Due to the limited size of most extensions, the easiest way to migrate the code is by
transplanting it into a new [repository created from this
template](#create-an-extension).

If the extension previously used a build tool other than uv, add any dependencies to
`pyproject.toml` by running `uv add <package-name>` in the project's root directory.

Next, make the code comply with the template's linters. In your terminal, run:

```bash
make install
make lint
```

Resolve any errors listed in the output. You can streamline this process by configuring
your text editor to highlight ruff, pyright, and mypy errors.

All extensions are expected to be well-tested. Once you have either migrated
existing tests or written new ones, run the full testing suite with:

```bash
make test
```

You can also generate a code coverage report with:

```bash
make test-coverage
```

Once everything passes, the extension's migration is complete.

## Publish the extension

To publish your extension, first configure trusted publishing on PyPI by
following [these
instructions](https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/#configuring-trusted-publishing).

Once that's done, push a signed [semantic versioning](https://semver.org/) tag to
publish the extension to PyPI. For example, if you were release version 1.2.3 of the
extension, you would run:

```bash
git tag -s -m "Release 1.2.3" "1.2.3"
git push --tags
```

## License and copyright

This template is released under the [GPL-3.0 license](LICENSE).

© 2025 Canonical Ltd.
