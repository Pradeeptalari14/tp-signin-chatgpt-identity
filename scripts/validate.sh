#!/usr/bin/env bash
set -euo pipefail

echo "=================================================="
echo " Validating Sign in with ChatGPT Identity Gateway"
echo "=================================================="

python3 -m py_compile oidc_token_verifier.py
python3 -m py_compile chatgpt_auth_middleware.py

python3 oidc_token_verifier.py
python3 chatgpt_auth_middleware.py

echo "Validation successful!"
