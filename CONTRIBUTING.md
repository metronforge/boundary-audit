# Contributing

## Commit messages and versioning

This project uses [Conventional Commits](https://www.conventionalcommits.org/)
and Semantic Versioning. Keep the Git history linear and rebase branches before
they are integrated into `main`.

Use commit messages in this form:

```text
<type>(optional-scope): <description>
```

The release impact is:

- `fix:` and `perf:` increment the patch version;
- `feat:` increments the minor version;
- `BREAKING CHANGE:` in the footer or `!` after the type/scope increments the
  major version;
- `build:`, `chore:`, `ci:`, `docs:`, `refactor:`, `style:`, and `test:` do not
  create a release on their own.

Examples:

```text
fix(metrics): handle an empty boundary set
feat(null-models): add conditional permutation
feat(api)!: replace the comparison result schema
```

On every push to `main`, Python Semantic Release analyzes commits since the
latest release, updates the version in `pyproject.toml`, updates `CHANGELOG.md`,
creates the Git tag and GitHub Release, and attaches the wheel and source
distribution.
