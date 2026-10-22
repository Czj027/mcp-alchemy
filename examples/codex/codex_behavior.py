"""Opt-in Codex integration; normal runs replay a synthetic SQLite observation."""

from pathlib import Path


def test_parameterized_sqlite_query(codex, tmp_path):
    project = tmp_path / "project"
    project.mkdir()
    source = Path(__file__).resolve().parents[2] / "mcp_alchemy"
    for path in source.rglob("*.py"):
        target = project / "mcp_alchemy" / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(path.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    (project / "bootstrap.py").write_text(
        "import os, sqlite3\n"
        'with sqlite3.connect("fixture.sqlite") as db:\n'
        '    db.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT)")\n'
        '    db.execute("INSERT INTO items VALUES (1, ?)", ("offline-demo",))\n'
        'os.environ["DB_URL"] = "sqlite:///fixture.sqlite"\n'
        'os.environ.pop("DB_ENGINE_OPTIONS", None)\n'
        'os.environ.pop("CLAUDE_LOCAL_FILES_PATH", None)\n'
        "from mcp_alchemy.server import main\n"
        "main()\n",
        encoding="utf-8",
        newline="\n",
    )
    run = codex.exec(
        "Use only the alchemy MCP execute_query tool once. Run exactly "
        'SELECT name FROM items WHERE id = :id with params {"id": 1}. '
        "Report the returned name. Do not execute shell commands or edit files.",
        project=project,
        model="gpt-6-luna",
        config={
            "model_reasoning_effort": "low",
            "mcp_servers.alchemy.command": "python",
            "mcp_servers.alchemy.args": ["bootstrap.py"],
            "mcp_servers.alchemy.enabled_tools": ["execute_query"],
            "mcp_servers.alchemy.tools.execute_query.approval_mode": "approve",
        },
    )
    assert run.succeeded, run
    assert run.called_mcp("alchemy", "execute_query"), run
    calls = [call for call in run.mcp_calls if call.server == "alchemy"]
    assert len(calls) == 1, run
    call = calls[0]
    assert call.arguments == {
        "query": "SELECT name FROM items WHERE id = :id",
        "params": {"id": 1},
    }, run
    assert call.status == "completed" and call.error is None, run
    assert call.result and not call.result.get("isError", False), run
    text = "\n".join(item.get("text", "") for item in call.result["content"])
    assert "name: offline-demo" in text and "Result: 1 rows" in text, run
    assert "offline-demo" in run.final_message, run
    assert not run.commands, run
    assert set(run.changed_files) <= {"fixture.sqlite"}, run
