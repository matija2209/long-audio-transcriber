#!/bin/bash -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

cat <<END > "$SCRIPT_DIR/.env"
WHISPER_API_KEY=<our openai key>
UID=$(id -u)
GID=$(id -g)
AUDIO_PATH=/app/input.mp4
END

