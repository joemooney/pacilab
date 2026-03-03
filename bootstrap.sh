#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")"

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements-dev.txt

echo ""
echo "paciLab bootstrap complete."
echo "Activate with: source .venv/bin/activate"
echo "Then run: make validate && make sim-regress REGRESS_COUNT=20 && make sim-topology"
