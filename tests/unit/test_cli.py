"""Tests for the runnable ECHO foundation."""

from echo.cli import main


def test_cli_reports_project_identity(capsys) -> None:
    """The initial entry point identifies ECHO and exits successfully."""
    assert main([]) == 0
    output = capsys.readouterr().out
    assert "ECHO - Attack Chain Reconstruction Engine" in output
    assert "Master Prompt 2" in output


def test_cli_generates_and_reconstructs_json(tmp_path, capsys) -> None:
    """The local CLI can produce and consume a synthetic scenario."""
    scenario_path = tmp_path / "scenario.json"
    graph_path = tmp_path / "graph.json"
    assert main(["generate", "--output", str(scenario_path), "--seed", "11"]) == 0
    assert main(["reconstruct", "--input", str(scenario_path), "--output", str(graph_path)]) == 0
    assert graph_path.exists()
    assert "Reconstructed" in capsys.readouterr().out
