# cz-github-conventional

A plugin for [commitizen](https://github.com/commitizen-tools/commitizen) that produces
[conventional commits](https://www.conventionalcommits.org/) whose scope carries GitHub issue
numbers, and links those issues in the generated `CHANGELOG.md`.

It is the GitHub successor of `cz-azure-devops-conventional` and keeps its bump rules:

| Commit type | Bump (major version ≥ 1) | Bump (major version 0) |
|---|---|---|
| `BREAKING CHANGE` | major | minor |
| `feat` | minor | minor |
| everything else (`fix`, `refactor`, `perf`, `style`, `test`, `docs`, `build`, `ci`, `chore`) | patch | patch |

So every push to a release branch yields a new version.

## Usage

```
> cz commit
? Select the type of change you are committing  fix: A bug fix. Correlates with PATCH in SemVer
? GitHub issue number (multiple "42, 123", press [enter] to skip).  42
...
```

produces `fix(#42): ...`. With `cz bump --changelog` the entry becomes
`**[#42](https://github.com/<owner>/<repo>/issues/42)**: ...` when the repository is known,
otherwise it stays `#42`, which GitHub auto-links anyway.

The repository is taken from the `github_repository` config key, or from the
`GITHUB_REPOSITORY` environment variable that GitHub Actions sets.

## Installation

```bash
uv tool install commitizen --with git+https://github.com/ACUAOcean/cz-github-conventional
```

or `pip install git+https://github.com/ACUAOcean/cz-github-conventional`.

Example `pyproject.toml` section:

```toml
[tool.commitizen]
name = "cz_github_conventional"
tag_format = "$version"
version_scheme = "semver2"
version_provider = "pep621"
major_version_zero = true
bump_message = "bump: version $current_version → $new_version [skip ci]"
# optional, defaults to $GITHUB_REPOSITORY in CI
github_repository = "ACUAOcean/my-repo"
```

## License

MIT.
