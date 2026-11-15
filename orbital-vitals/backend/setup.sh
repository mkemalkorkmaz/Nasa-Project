#!/usr/bin/env bash
# Debian-friendly setup: creates a venv with a MediaPipe-compatible Python (3.9-3.11).
set -e
cd "$(dirname "$0")"

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv (fast Python/venv manager) ..."
  sudo apt-get update && sudo apt-get install -y curl ca-certificates libgl1 libglib2.0-0
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="$HOME/.local/bin:$PATH"
fi

uv venv --python 3.11 .venv      # downloads Python 3.11 automatically if missing
uv pip install --python .venv/bin/python -r requirements.txt
echo
echo "Done. Start the backend with:  .venv/bin/python app.py"
