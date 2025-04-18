# Code Comment Remover

A simple yet powerful Python utility to remove comments from source code files across various programming languages. Useful for code analysis, compression, or simply getting a clearer view of logic without distractions.

## Features

- Detects and removes comments from **14 different programming language styles**
- Supports both **single-line** and **multi-line** comments
- Works via **command-line arguments** or **interactive prompts**
- Outputs a clean file with comments stripped (`_nocomments` suffix)

## Supported Languages

- `c-style` (C, C++, Java, etc.)
- `html`
- `python`
- `hash-style` (Bash, YAML)
- `semicolon-style` (Assembly-like)
- `percent-style` (MATLAB, TeX)
- `ada`
- `haskell`
- `lua`
- `delphi`
- `cobol`
- `sas`
- `vbnet`
- `abap`

## Usage

### CLI Arguments

```bash
python remove_comments.py -i path/to/code.ext -c language
