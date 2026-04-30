# eng-linux-cmd

A command-line tool that translates plain English descriptions into Linux shell commands using a locally-running LLM. No API key or internet connection required after the initial model download.

---

## Features

- **Natural language → Linux command** translation via a local LLM
- **Command explanation** (`--explain`) — breaks down every flag and token in plain English
- **Security validation** — blocks dangerous commands (e.g. `rm -rf /`, fork bombs) before execution
- **Context-aware prompting** — the model knows your current user, working directory, files, OS, and system time
- **Persistent chat history** — maintains conversation context across queries within a session
- **Multiple model support** — choose from four quantized GGUF models (auto-downloaded on first use)
- **Interactive confirmation** — always asks before executing a generated command

---

## Supported Platforms

| Platform | Supported |
|----------|-----------|
| macOS    | Yes       |
| Linux    | Yes       |
| Windows  | No        |

---

## Installation

### Option 1: Install from GitHub Release (Recommended for Grading)
```bash
pip install https://github.com/Dread63/cs3300-eng-linux-cmd/releases/download/release-v0.1.3/eng_linux_cmd-0.1.3-py3-none-any.whl
```

### Option 2: Install from Source (Editable Mode)
```bash
git clone https://github.com/Dread63/cs3300-eng-linux-cmd.git
cd cs3300-eng-linux-cmd
pip install -e .
```

---

## Usage

After installation, the tool is available as `en-linux`.

```bash
# Interactive mode — enter requests one at a time, type 'exit' or 'quit' to stop
en-linux

# One-shot query
en-linux "list all files sorted by size"

# Specify a model (downloads automatically if not present)
en-linux --model qwen2.5-1.5b "find all log files modified today"
en-linux -m qwen2.5-1.5b "find all log files modified today"

# Enable command explanation
en-linux --explain "show disk usage sorted by size"
en-linux -e "show disk usage sorted by size"

# Combine flags
en-linux -m qwen2.5-1.5b -e "count the number of running processes"
```

### Example Session

```
$ en-linux "show me all hidden files"

Command: ls -la | grep '^\.'
Confidence: high

Run command? (y/N): y
.bashrc
.gitconfig
...
```

With `--explain`:
```
$ en-linux -e "show disk usage and sort by size"

Command: du -sh * | sort -rh
Confidence: high

SUMMARY: Shows disk usage for each item in the current directory, sorted largest first.
BREAKDOWN:
  du -sh *: report disk usage in human-readable format for each item
  sort -rh: sort in reverse order, treating sizes as human-readable numbers

Run command? (y/N):
```

---

## Available Models

The first time you run `en-linux`, you will be prompted to select a model. It downloads automatically. You can also pass `--model` to select or switch models.

| Model Key            | Size    | RAM Required | Best For                        |
|----------------------|---------|--------------|----------------------------------|
| `qwen2.5-0.5b`       | ~0.5B   | ~0.5–1 GB    | Fast inference, low-resource machines |
| `qwen2.5-1.5b`       | 1.5B    | ~1.5–3 GB    | Better reasoning, recommended default |
| `gemma-2b`           | ~2B     | ~2–4 GB      | General-purpose, Google's model  |
| `deepseek-coder-1.3b`| 1.3B    | ~1.5–3 GB    | Code-specialized                 |

Model files are stored at:
- **macOS**: `~/Library/Application Support/eng-linux-cmd/`
- **Linux**: `~/.local/share/eng-linux-cmd/`

---

## Running the Tests

The test suite runs 100 translation tests across 10 categories without executing any generated commands.

```bash
cd tests
python test_testCases.py
```

> **Note:** You must have a model downloaded (i.e. have run `en-linux` at least once) before running the tests, as they use the same model initialization.

### Test Categories

| Category                     | Tests | Description                                      |
|------------------------------|-------|--------------------------------------------------|
| Simple                       | 10    | Single-word commands (`ls`, `pwd`, `whoami`)     |
| Intermediate                 | 10    | Commands with flags (`ls -la`, `chmod 755`)      |
| Two Step                     | 10    | Piped or chained commands                        |
| More Steps                   | 10    | Three or more chained commands                   |
| Mathematical                 | 10    | Arithmetic using shell (`echo $((5+3))`, `bc`)   |
| System Functions             | 10    | File/directory operations (`cp`, `mv`, `chmod`)  |
| Blocked Commands             | 10    | Dangerous commands that should be rejected       |
| Hardly English               | 10    | Vague or broken English inputs                   |
| Mathematical System Functions| 10    | Math applied to system data (file counts, sizes) |
| Advanced                     | 10    | Complex multi-tool commands                      |

### Test Output

Results print to the terminal and are saved to `tests/test_results_detailed.txt`. Each test shows:
- The generated command vs. the expected command
- A similarity score (0–100%)
- Pass/Fail (threshold: ≥ 80% similarity)
- A final grade for the model's overall performance

---

## Project Structure

```
cs3300-eng-linux-cmd/
├── src/
│   ├── cli.py           # CLI entry point and flag definitions (Typer)
│   ├── main.py          # Main interactive loop
│   ├── ollama_client.py # LLM initialization, model download, and inference
│   ├── explainer.py     # Command explanation via the LLM
│   ├── security.py      # Command validation and shell state handling
│   └── terminal_ui.py   # Rich terminal UI (banners, spinners, formatting)
├── tests/
│   ├── test_testCases.py          # 100-case test suite
│   └── test_results_detailed.txt  # Last saved test run output
├── environment.yml   # Conda environment definition
├── pyproject.toml    # Package metadata and dependencies
└── README.md
```

---

## Development Setup

### Initial Setup
1. Clone the repository
2. Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html)
3. From the project root, create the environment:
   ```bash
   conda env create -f environment.yml
   ```
4. Verify with `conda env list` — you should see `eng-linux-cmd` listed
5. Activate the environment:
   ```bash
   conda activate eng-linux-cmd
   ```
6. Install the package in editable mode:
   ```bash
   pip install -e .
   ```

### Updating the Conda Environment
```bash
conda activate eng-linux-cmd
conda env update -f environment.yml
```

---

## Dependencies

| Package             | Purpose                                      |
|---------------------|----------------------------------------------|
| `typer`             | CLI flag parsing                             |
| `rich`              | Terminal formatting and UI                   |
| `llama-cpp-python`  | Local LLM inference (GGUF format)            |
| `requests`          | Model file download                          |
| `clint`             | Download progress bar                        |
| `huggingface-hub`   | HuggingFace model registry access            |
