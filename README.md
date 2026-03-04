# Vyper Language Server

A language server for [Vyper](https://github.com/vyperlang/vyper), a pythonic smart contract language for the EVM.

Forked from [vyperlang/vyper-lsp](https://github.com/vyperlang/vyper-lsp).

## Requirements

- Python >= 3.12
- Vyper >= 0.4.1

The Vyper version installed in your virtual environment must be capable of compiling your contract for full support.

## Installation

This language server imports Vyper as a library, so it should be installed in the same environment as your project's Vyper.

### As a project dev dependency (recommended)

```toml
# pyproject.toml
[dependency-groups]
dev = [
    "vyper-language-server",
]

[tool.uv.sources]
vyper-language-server = { git = "https://github.com/latticafi/vyper-language-server" }
```

Then `uv sync`.

### Via pipx (global)

```bash
pipx install git+https://github.com/latticafi/vyper-language-server.git
```

Note: when installed globally, the server will use whatever Vyper version is in its own environment, which may not match your project.

### Verify

```bash
which vyper-language-server
```

## Editor Setup

### Neovim

Add to `~/.config/nvim/init.lua`:

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "*.vy" },
  callback = function()
    vim.lsp.start({
      name = "vyper-language-server",
      cmd = { "vyper-language-server" },
      root_dir = vim.fs.dirname(vim.fs.find({ ".git" }, { upward = true })[1])
    })
  end,
})
```

If installed as a project dep, point to the venv binary:

```lua
vim.api.nvim_create_autocmd({ "BufEnter" }, {
  pattern = { "*.vy" },
  callback = function()
    local venv = vim.fs.find({ ".venv" }, { upward = true })[1]
    local cmd = venv and (venv .. "/bin/vyper-language-server") or "vyper-language-server"
    vim.lsp.start({
      name = "vyper-language-server",
      cmd = { cmd },
      root_dir = vim.fs.dirname(vim.fs.find({ ".git" }, { upward = true })[1])
    })
  end,
})
```

### Emacs

```emacs-lisp
(define-derived-mode vyper-mode python-mode "Vyper" "Major mode for editing Vyper.")

(add-to-list 'auto-mode-alist '("\\.vy\\'" . vyper-mode))

(with-eval-after-load 'lsp-mode
  (add-to-list 'lsp-language-id-configuration
               '(vyper-mode . "vyper"))
  (lsp-register-client
   (make-lsp-client :new-connection
                    (lsp-stdio-connection `(,(executable-find "vyper-language-server")))
                    :activation-fn (lsp-activate-on "vyper")
                    :server-id 'vyper-language-server)))
```

## Features

- Diagnostics (compile errors and warnings)
- Completions (state variables, functions, decorators, types, imports)
- Hover information
- Go to definition / declaration
- Find references
- Signature help

## Development

### Setup

1. **Install uv** (Fast Python package installer and resolver)

```bash
   pip install uv
   # Or on macOS with Homebrew
   brew install uv
```

2. **Clone and install**

```bash
   git clone https://github.com/latticafi/vyper-language-server.git
   cd vyper-language-server
   uv sync
```

### Commands

```bash
uv run pytest                  # run tests
uv run ruff check .            # lint
uv run ruff format .           # format
uv run coverage run -m pytest  # test with coverage
uv run coverage report         # view coverage
```

## License

MIT
