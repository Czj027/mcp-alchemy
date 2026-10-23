# Optional Codex behavior example

This example checks that Codex calls MCP Alchemy's real `execute_query` tool
with a parameterized query and reports the returned value. It creates a tiny
SQLite database with one synthetic row; it never uses `tests/Chinook_Sqlite.sqlite`
or an existing database connection. The launcher overrides `DB_URL` and removes
optional engine/export settings in its own process.

From the repository root, in a virtual environment:

```console
python -m pip install -r examples/codex/requirements.txt
python -m pytest -c examples/codex/pytest.ini examples/codex --codex-bin=not-installed -q
```

Replay requires neither the MCP SDK nor SQLAlchemy, a Codex binary, login or model
calls. It restores and checks a saved observation; it does not start today's
server. The example has a separate pytest configuration and a non-default file
name so it does not join ordinary test discovery or add a runtime dependency.

To make a fresh observation, install `requirements-live.txt`, activate that
environment so `python` resolves to it, and use a logged-in Codex CLI 0.163.0:

```console
python -m pip install -r examples/codex/requirements-live.txt
python -m pytest -c examples/codex/pytest.ini examples/codex --codex-record -q
```

Recording consumes model quota and uses `gpt-6-luna`. It exposes only
`execute_query` and approves that one tool inside this disposable fixture's
test process. It does not change your global Codex configuration. Review these
settings before recording; do not adapt this bootstrap to a production database.

The test copies the current Python implementation with normalized line endings;
source changes invalidate replay and require an intentional re-record. It checks
tool arguments, status, result content, final answer, absence of shell commands
and absence of changes outside the generated database.

## Recorded evidence

- Upstream source: `8df3eb56773fdbb71eb3b7e509fefa312b16793b`.
- Recorded on Windows, Python 3.13, Codex CLI 0.163.0, MCP SDK 2.3.0 and
  SQLAlchemy 2.0.36. One successful observation, not a reliability estimate.
- First setup attempt was denied by tool approval policy; the test failed.
  The committed observation was recorded after scoping approval to this fixture.
- Thread identifier anonymized; nonbehavioral startup stderr omitted. Tool
  arguments, results, usage, file diff and synthetic database bytes are retained.
- Ordinary replay is offline; re-record to assess a new model or server version.

## Personal-fork compatibility check

This branch is maintained by the pytest-codex author as a personal-fork case
study. It is not upstream adoption, endorsement, or an independently reported
user trial. The original recording is unchanged; replay now uses the published
pytest-codex 0.3.0 package.

The separate `Offline Codex replay` workflow runs on Linux, macOS and Windows
with Python 3.10 and 3.13. It installs only replay dependencies and explicitly
selects an unavailable Codex executable. It cannot make a fresh model call.
A green run verifies the saved observation and restored fixture artifacts; it
does not start the current MCP server or prove fresh model compatibility.
Dependency installation needs network access; test execution replays locally.
There is no scheduled live testing or model spend.
