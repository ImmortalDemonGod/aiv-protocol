"""
Tests for aiv.hooks.pre_commit — the portable pre-commit hook.

Tests the rule engine directly by mocking _staged_files and _run_git,
without requiring an actual git repository.
"""

from __future__ import annotations

from unittest.mock import patch

from aiv.hooks.pre_commit import (
    _DEFAULT_FUNCTIONAL_PREFIXES,
    _DEFAULT_FUNCTIONAL_ROOT_FILES,
    _is_functional,
    _is_gitkeep,
    _is_packet,
    _is_submodule_path,
    _load_hook_config,
    _validate_packet,
    main,
)

# ---------------------------------------------------------------------------
# Classification tests
# ---------------------------------------------------------------------------


class TestIsPacket:
    def test_standard_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_AUTH_FIX.md") is True

    def test_legacy_location(self) -> None:
        assert _is_packet(".github/VERIFICATION_PACKET_OLD.md") is True

    def test_template_is_not_packet(self) -> None:
        # Templates match the pattern — they ARE packets structurally
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_TEMPLATE.md") is True

    def test_random_markdown_not_packet(self) -> None:
        assert _is_packet("README.md") is False
        assert _is_packet(".github/aiv-packets/README.md") is False

    def test_non_md_not_packet(self) -> None:
        assert _is_packet(".github/aiv-packets/VERIFICATION_PACKET_FOO.txt") is False


class TestIsFunctional:
    def test_src_file(self) -> None:
        assert _is_functional("src/aiv/cli/main.py") is True

    def test_test_file(self) -> None:
        assert _is_functional("tests/unit/test_parser.py") is True

    def test_workflow(self) -> None:
        assert _is_functional(".github/workflows/ci.yml") is True

    def test_scripts(self) -> None:
        assert _is_functional("scripts/map_packets.py") is True

    def test_engine(self) -> None:
        assert _is_functional("engine/cli.ts") is True

    def test_root_config(self) -> None:
        assert _is_functional("pyproject.toml") is True
        assert _is_functional("package.json") is True
        assert _is_functional(".gitignore") is True

    def test_readme_not_functional(self) -> None:
        assert _is_functional("README.md") is False

    def test_docs_not_functional(self) -> None:
        assert _is_functional("docs/guide.md") is False

    def test_changelog_not_functional(self) -> None:
        assert _is_functional("CHANGELOG.md") is False

    def test_packet_not_functional(self) -> None:
        assert _is_functional(".github/aiv-packets/VERIFICATION_PACKET_FOO.md") is False


class TestIsGitkeep:
    def test_gitkeep(self) -> None:
        assert _is_gitkeep(".github/aiv-packets/.gitkeep") is True

    def test_other_gitkeep(self) -> None:
        assert _is_gitkeep("data/.gitkeep") is False


class TestIsSubmodulePath:
    def test_exact_match(self) -> None:
        assert _is_submodule_path("aiv-protocol", ["aiv-protocol"]) is True

    def test_nested_file(self) -> None:
        assert _is_submodule_path("aiv-protocol/src/foo.py", ["aiv-protocol"]) is True

    def test_no_match(self) -> None:
        assert _is_submodule_path("src/foo.py", ["aiv-protocol"]) is False

    def test_empty_submodules(self) -> None:
        assert _is_submodule_path("anything", []) is False


# ---------------------------------------------------------------------------
# Rule engine tests (mock git)
# ---------------------------------------------------------------------------


def _mock_main(staged: list[str], submodule_paths: list[str] | None = None, hook_config: tuple | None = None) -> int:
    """Run main() with mocked staged files and no packet validation."""
    cfg = hook_config or (_DEFAULT_FUNCTIONAL_PREFIXES, _DEFAULT_FUNCTIONAL_ROOT_FILES)
    with (
        patch("aiv.hooks.pre_commit._staged_files", return_value=staged),
        patch("aiv.hooks.pre_commit._write_safety_snapshot"),
        patch("aiv.hooks.pre_commit._run_git", return_value=""),
        patch("aiv.hooks.pre_commit._validate_packet", return_value=True),
        patch(
            "aiv.hooks.pre_commit._get_submodule_paths",
            return_value=submodule_paths or [],
        ),
        patch("aiv.hooks.pre_commit._load_hook_config", return_value=cfg),
    ):
        return main()


class TestRule1DependencyPair:
    def test_package_json_pair_allowed(self) -> None:
        assert _mock_main(["package.json", "package-lock.json"]) == 0

    def test_package_json_alone_needs_packet(self) -> None:
        # package.json is functional → needs a packet
        assert _mock_main(["package.json"]) == 1


class TestRule2AtomicUnit:
    def test_functional_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    "src/aiv/cli/main.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_CLI_FIX.md",
                ]
            )
            == 0
        )

    def test_test_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    "tests/unit/test_parser.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_PARSER.md",
                ]
            )
            == 0
        )

    def test_functional_plus_packet_validates(self) -> None:
        """When packet validation fails, commit is rejected."""
        with (
            patch(
                "aiv.hooks.pre_commit._staged_files",
                return_value=[
                    "src/aiv/cli/main.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_CLI_FIX.md",
                ],
            ),
            patch("aiv.hooks.pre_commit._write_safety_snapshot"),
            patch("aiv.hooks.pre_commit._run_git", return_value=""),
            patch("aiv.hooks.pre_commit._validate_packet", return_value=False),
            patch("aiv.hooks.pre_commit._get_submodule_paths", return_value=[]),
        ):
            assert main() == 1


class TestRule3PacketPlusGitkeep:
    def test_packet_plus_gitkeep_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    ".github/aiv-packets/.gitkeep",
                    ".github/aiv-packets/VERIFICATION_PACKET_INIT.md",
                ]
            )
            == 0
        )


class TestRule4SubmoduleUpdate:
    def test_submodule_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                ["aiv-protocol", ".github/aiv-packets/VERIFICATION_PACKET_SUBMOD.md"],
                submodule_paths=["aiv-protocol"],
            )
            == 0
        )


class TestRule5SubmoduleAdd:
    def test_gitmodules_plus_submodule_plus_packet_allowed(self) -> None:
        assert (
            _mock_main(
                [
                    ".gitmodules",
                    "aiv-protocol",
                    ".github/aiv-packets/VERIFICATION_PACKET_SUBMOD_ADD.md",
                ],
                submodule_paths=["aiv-protocol"],
            )
            == 0
        )


class TestRule6PacketOnly:
    def test_single_packet_allowed(self) -> None:
        assert _mock_main([".github/aiv-packets/VERIFICATION_PACKET_DOCS.md"]) == 0


class TestRule7DocsOnly:
    def test_readme_only_allowed(self) -> None:
        assert _mock_main(["README.md"]) == 0

    def test_changelog_only_allowed(self) -> None:
        assert _mock_main(["CHANGELOG.md"]) == 0

    def test_docs_file_allowed(self) -> None:
        assert _mock_main(["docs/guide.md"]) == 0

    def test_multiple_docs_allowed(self) -> None:
        assert _mock_main(["README.md", "CHANGELOG.md", "docs/guide.md"]) == 0


class TestRule8TooManyFiles:
    def test_three_functional_files_rejected(self) -> None:
        assert (
            _mock_main(
                [
                    "src/a.py",
                    "src/b.py",
                    ".github/aiv-packets/VERIFICATION_PACKET_FOO.md",
                ]
            )
            == 1
        )


class TestRule9FunctionalWithoutPacket:
    def test_src_without_packet_rejected(self) -> None:
        assert _mock_main(["src/aiv/cli/main.py"]) == 1

    def test_pyproject_without_packet_rejected(self) -> None:
        assert _mock_main(["pyproject.toml"]) == 1

    def test_workflow_without_packet_rejected(self) -> None:
        assert _mock_main([".github/workflows/ci.yml"]) == 1


class TestRule10InvalidTwoFileCombination:
    def test_two_functional_files_rejected(self) -> None:
        assert _mock_main(["src/a.py", "src/b.py"]) == 1

    def test_two_docs_files_allowed(self) -> None:
        # Two non-functional files → Rule 7 (docs-only) allows
        assert _mock_main(["README.md", "CHANGELOG.md"]) == 0


class TestEmptyStaged:
    def test_nothing_staged_allowed(self) -> None:
        assert _mock_main([]) == 0


# ---------------------------------------------------------------------------
# P0-1: Configurable functional prefixes
# ---------------------------------------------------------------------------


class TestConfigurablePrefixes:
    """Verify that _is_functional respects custom prefixes and root files."""

    def test_lib_is_functional_by_default(self) -> None:
        """P0-1 fix: lib/ should be functional with new defaults."""
        assert _is_functional("lib/mycode.py") is True

    def test_app_is_functional_by_default(self) -> None:
        assert _is_functional("app/main.py") is True

    def test_pkg_is_functional_by_default(self) -> None:
        assert _is_functional("pkg/server.go") is True

    def test_custom_prefix_overrides_defaults(self) -> None:
        custom_prefixes = ("my_code/",)
        custom_roots = set()
        assert _is_functional("my_code/foo.py", custom_prefixes, custom_roots) is True
        assert _is_functional("src/bar.py", custom_prefixes, custom_roots) is False

    def test_custom_root_files(self) -> None:
        custom_prefixes = ()
        custom_roots = {"Makefile", "Dockerfile"}
        assert _is_functional("Makefile", custom_prefixes, custom_roots) is True
        assert _is_functional("Dockerfile", custom_prefixes, custom_roots) is True
        assert _is_functional("pyproject.toml", custom_prefixes, custom_roots) is False

    def test_project_specific_artifacts_removed(self) -> None:
        """P0-2: astro.config.mjs and tailwind.config.js should NOT be in defaults."""
        assert "astro.config.mjs" not in _DEFAULT_FUNCTIONAL_ROOT_FILES
        assert "tailwind.config.js" not in _DEFAULT_FUNCTIONAL_ROOT_FILES

    def test_hook_engine_uses_custom_config(self) -> None:
        """Integration: main() should use custom prefixes from config."""
        custom = (("backend/",), {"Makefile"})
        # backend/app.py is functional with custom config → needs packet → rejected
        assert _mock_main(["backend/app.py"], hook_config=custom) == 1
        # src/app.py is NOT functional with custom config → docs-only → allowed
        assert _mock_main(["src/app.py"], hook_config=custom) == 0


class TestLoadHookConfig:
    """Tests for _load_hook_config reading .aiv.yml."""

    def test_returns_defaults_when_no_file(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        prefixes, root_files = _load_hook_config()
        assert prefixes == _DEFAULT_FUNCTIONAL_PREFIXES
        assert root_files == _DEFAULT_FUNCTIONAL_ROOT_FILES

    def test_reads_custom_prefixes_from_yaml(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".aiv.yml").write_text(
            'version: "1.0"\nhook:\n  functional_prefixes:\n    - "backend/"\n    - "frontend/"\n',
            encoding="utf-8",
        )
        prefixes, root_files = _load_hook_config()
        assert prefixes == ("backend/", "frontend/")
        # root_files should fall back to defaults when not specified
        assert root_files == _DEFAULT_FUNCTIONAL_ROOT_FILES

    def test_reads_custom_root_files_from_yaml(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".aiv.yml").write_text(
            'version: "1.0"\nhook:\n  functional_root_files:\n    - "Makefile"\n    - "Dockerfile"\n',
            encoding="utf-8",
        )
        prefixes, root_files = _load_hook_config()
        assert prefixes == _DEFAULT_FUNCTIONAL_PREFIXES
        assert root_files == {"Makefile", "Dockerfile"}

    def test_returns_defaults_for_empty_hook_section(self, tmp_path, monkeypatch) -> None:
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".aiv.yml").write_text(
            'version: "1.0"\nhook: {}\n',
            encoding="utf-8",
        )
        prefixes, root_files = _load_hook_config()
        assert prefixes == _DEFAULT_FUNCTIONAL_PREFIXES
        assert root_files == _DEFAULT_FUNCTIONAL_ROOT_FILES

    def test_string_prefixes_falls_back_to_defaults(self, tmp_path, monkeypatch) -> None:
        """SVP probe: string value for functional_prefixes should not be character-split."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".aiv.yml").write_text(
            'version: "1.0"\nhook:\n  functional_prefixes: "src/"\n',
            encoding="utf-8",
        )
        prefixes, root_files = _load_hook_config()
        assert prefixes == _DEFAULT_FUNCTIONAL_PREFIXES
        assert "s" not in prefixes


# ---------------------------------------------------------------------------
# F43 / F113 - fail-closed packet validation (regression: exception != skip)
# ---------------------------------------------------------------------------


class TestValidatePacketFailsClosed:
    """F43: an exception inside _validate_packet must BLOCK the commit, not skip it.

    The pre-fix code did ``except Exception: return True``, so a crashed validator
    (aiv check missing, git failure, tempfile error) silently passed the commit -
    the enforcement gate failed OPEN. The gate must fail CLOSED.
    """

    def test_validate_packet_returns_false_on_internal_exception(self) -> None:
        # The first thing _validate_packet does is _run_git("show", ...); force it to raise.
        with patch(
            "aiv.hooks.pre_commit._run_git",
            side_effect=RuntimeError("forced validation crash"),
        ):
            assert _validate_packet(".github/aiv-packets/VERIFICATION_PACKET_X.md") is False

    def test_main_blocks_commit_when_validation_raises(self) -> None:
        # Goal condition (F43 recipe): a forced exception inside _validate_packet
        # makes main() block the commit with a non-zero exit.
        staged = ["src/aiv/cli/main.py", ".github/aiv-packets/VERIFICATION_PACKET_X.md"]
        with (
            patch("aiv.hooks.pre_commit._staged_files", return_value=staged),
            patch("aiv.hooks.pre_commit._write_safety_snapshot"),
            patch("aiv.hooks.pre_commit._get_submodule_paths", return_value=[]),
            patch(
                "aiv.hooks.pre_commit._load_hook_config",
                return_value=(_DEFAULT_FUNCTIONAL_PREFIXES, _DEFAULT_FUNCTIONAL_ROOT_FILES),
            ),
            patch(
                "aiv.hooks.pre_commit._run_git",
                side_effect=RuntimeError("forced validation crash"),
            ),
        ):
            assert main() == 1
