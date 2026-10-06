#!/bin/bash
# Both original entry points use the same complete export pipeline.
set -euo pipefail
cd "$(dirname "$0")"
exec bash ./打包整合包.command
