# Installation

### Option 1: Install from GitHub Release (Alpha)
You can install the latest alpha release directly from GitHub:

```bash
pip install https://github.com/Dread63/cs3300-eng-linux-cmd/releases/tag/Alpha-release-1-Pip-install-working/eng_linux_cmd-0.1.0a1-py3-none-any.whl
```

### Option 2: Install from Source (Editable Mode)
If you want to contribute or test changes locally:

1. Clone the repository:
   ```bash
   git clone https://github.com/Dread63/cs3300-eng-linux-cmd.git
   cd eng-linux-cmd
   ```

2. Install in editable mode:
   ```bash
   pip install -e .
   ```

# Development Setup
### Initial Setup
1) Clone the repo to you local device in whatever dev directory you usually use
2) Install [conda](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html) utilizing whichever method makes most sense for you specific hardware/OS
3) Open a terminal and navigate to the project root directory, run `conda env create -f environment.yml`
4) Ensure the installation of the conda environment completed successfully by running `conda env list`
    > You should see eng-linux-cmd listed as an available conda environment
5) Activate the conda environment by running `conda activate eng-linux-cmd` in either your terminal or selecting it in your IDE

# Updating Conda Environment
1) Open a terminal and navigate to the root directory of the project
2) Activate the en-linux conda envrionment within the terminal
3) Run `conda env update -f environment.yml`
