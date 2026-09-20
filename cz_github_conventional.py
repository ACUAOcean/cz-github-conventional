from __future__ import annotations

import os
import re
from typing import TYPE_CHECKING, Any

from commitizen.cz.base import BaseCommitizen
from commitizen.cz.conventional_commits import ConventionalCommitsCz
from commitizen.cz.exceptions import CzException
from commitizen.cz.utils import multiple_line_breaker, required_validator
from commitizen.defaults import BUMP_PATTERN, MAJOR, MINOR, PATCH

if TYPE_CHECKING:
    from commitizen import git

__all__ = ["GithubConventionalCz"]

DEFAULT_CHANGE_TYPE_MAP = {
    "feat": "Feat",
    "fix": "Fix",
    "refactor": "Refactor",
    "perf": "Perf",
}


def parse_subject(text):
    if isinstance(text, str):
        text = text.strip(".").strip()

    return required_validator(text, msg="Subject is required.")


class GithubConventionalCz(BaseCommitizen):
    """Conventional commits with GitHub issue references in the scope.

    Every commit type bumps the version by at least a patch, so any push to a
    release branch produces a new version.
    """

    bump_pattern = BUMP_PATTERN

    # bump all changes by at least patch level
    bump_map = {
        "BREAKING CHANGE": MAJOR,
        "feat": MINOR,
        "fix": PATCH,
        "refactor": PATCH,
        "perf": PATCH,
        "style": PATCH,
        "test": PATCH,
        "docs": PATCH,
        "build": PATCH,
        "ci": PATCH,
        "chore": PATCH,
    }

    bump_map_major_version_zero = {
        "BREAKING CHANGE": MINOR,
        "feat": MINOR,
        "fix": PATCH,
        "refactor": PATCH,
        "perf": PATCH,
        "style": PATCH,
        "test": PATCH,
        "docs": PATCH,
        "build": PATCH,
        "ci": PATCH,
        "chore": PATCH,
    }

    commit_parser = ConventionalCommitsCz.commit_parser
    changelog_pattern = BUMP_PATTERN
    issue_multiple_hint = "42, 123"
    change_type_map = DEFAULT_CHANGE_TYPE_MAP

    def questions(self) -> list[dict[str, Any]]:
        questions: list[dict[str, Any]] = [
            {
                "type": "list",
                "name": "prefix",
                "message": "Select the type of change you are committing",
                "choices": [
                    {
                        "value": "fix",
                        "name": "fix: A bug fix. Correlates with PATCH in SemVer",
                    },
                    {
                        "value": "feat",
                        "name": "feat: A new feature. Correlates with MINOR in SemVer",
                    },
                    {"value": "docs", "name": "docs: Documentation only changes"},
                    {
                        "value": "style",
                        "name": (
                            "style: Changes that do not affect the "
                            "meaning of the code (white-space, formatting,"
                            " missing semi-colons, etc)"
                        ),
                    },
                    {
                        "value": "refactor",
                        "name": (
                            "refactor: A code change that neither fixes "
                            "a bug nor adds a feature"
                        ),
                    },
                    {
                        "value": "perf",
                        "name": "perf: A code change that improves performance",
                    },
                    {
                        "value": "test",
                        "name": "test: Adding missing or correcting existing tests",
                    },
                    {
                        "value": "build",
                        "name": (
                            "build: Changes that affect the build system or "
                            "external dependencies (example scopes: pip, docker, npm)"
                        ),
                    },
                    {
                        "value": "ci",
                        "name": (
                            "ci: Changes to our CI configuration files and "
                            "scripts (example scopes: GitHub Actions)"
                        ),
                    },
                    {
                        "value": "chore",
                        "name": "chore: Other changes that don't modify source or test files",
                    },
                ],
            },
            {
                "type": "input",
                "name": "scope",
                "message": (
                    f'GitHub issue number (multiple "{self.issue_multiple_hint}", '
                    "press [enter] to skip)."
                ),
                "filter": self.parse_scope,
            },
            {
                "type": "input",
                "name": "subject",
                "filter": parse_subject,
                "message": (
                    "Write a short and imperative summary of the code changes: "
                    "(lower case and no period)\n"
                ),
            },
            {
                "type": "input",
                "name": "body",
                "message": (
                    "Provide additional contextual information about the code changes: "
                    "(press [enter] to skip)\n"
                ),
                "filter": multiple_line_breaker,
            },
            {
                "type": "confirm",
                "message": "Is this a BREAKING CHANGE? Correlates with MAJOR in SemVer",
                "name": "is_breaking_change",
                "default": False,
            },
            {
                "type": "input",
                "name": "footer",
                "message": (
                    "Footer. Information about Breaking Changes and "
                    "reference issues that this commit closes: (press [enter] to skip)\n"
                ),
            },
        ]
        return questions

    def parse_scope(self, text):
        """Validate the scope as a comma-separated list of GitHub issue numbers."""
        issue_re = re.compile(r"#?\d+")

        if not text:
            return []

        issues = [i.strip() for i in text.strip().split(",")]
        for issue in issues:
            if not issue_re.fullmatch(issue):
                raise InvalidAnswerError(f"GitHub issue '{issue}' is not valid.")

        return [i.lstrip("#") for i in issues]

    def message(self, answers: dict) -> str:
        prefix = answers["prefix"]
        issues = answers["scope"]
        subject = answers["subject"]
        body = answers["body"]
        footer = answers["footer"]
        is_breaking_change = answers["is_breaking_change"]

        scope = ""
        if issues:
            scope = "(" + ",".join("#" + i for i in issues) + ")"
        if body:
            body = f"\n\n{body}"
        if is_breaking_change:
            footer = f"BREAKING CHANGE: {footer}"
        if footer:
            footer = f"\n\n{footer}"

        return f"{prefix}{scope}: {subject}{body}{footer}"

    def example(self) -> str:
        return (
            "fix(#12): correct minor typos in code\n"
            "\n"
            "see the issue for details on the typos fixed\n"
            "\n"
            "closes issue #12"
        )

    def schema(self) -> str:
        return (
            "<type>(<#issue>[,<#issue>]): <subject>\n"
            "<BLANK LINE>\n"
            "<body>\n"
            "<BLANK LINE>\n"
            "(BREAKING CHANGE: )<footer>"
        )

    def schema_pattern(self) -> str:
        return (
            r"(build|ci|docs|feat|fix|perf|refactor|style|test|chore|revert|bump)"
            r"(\(\S+\))?!?:(\s.*)"
        )

    def info(self) -> str:
        return (
            "Conventional commits (https://www.conventionalcommits.org) where the "
            "scope holds GitHub issue numbers, e.g. `feat(#42,#123): add thing`.\n"
            "Every commit type bumps at least the patch version; `feat` bumps minor "
            "and `BREAKING CHANGE` bumps major (minor while the major version is 0).\n"
            "CHANGELOG entries link issues to the repository named by the "
            "`github_repository` config key or the GITHUB_REPOSITORY environment variable."
        )

    def process_commit(self, commit: str) -> str:
        m = re.match(self.schema_pattern(), commit)
        if m is None:
            return ""
        return m.group(3).strip()

    def _repository(self) -> str | None:
        return self.config.settings.get("github_repository") or os.environ.get(
            "GITHUB_REPOSITORY"
        )

    def changelog_message_builder_hook(
        self, parsed_message: dict[str, Any], commit: git.GitCommit
    ) -> dict[str, Any]:
        """Turn `#123` scopes into links to the repository's issues.

        Without a known repository the scope is left as-is; GitHub still
        auto-links `#123` when it renders the CHANGELOG.
        """
        repository = self._repository()
        if repository and parsed_message.get("scope"):
            parsed_message["scope"] = " ".join(
                f"[{issue}](https://github.com/{repository}/issues/{issue.lstrip('#')})"
                for issue in parsed_message["scope"].split(",")
            )
        return parsed_message


class InvalidAnswerError(CzException):
    ...
