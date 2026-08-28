#!/usr/bin/env bash
# ==============================================================================
# Animaker AI - Google Colab Environment Setup Script
# ==============================================================================
set -e

echo "🚀 [1/5] Removing outdated /tools/node and installing Node.js 20 LTS, FFmpeg, Redis..."
# Remove legacy Colab node tools that cause 'Cannot find module node:path'
rm -rf /tools/node 2>/dev/null || true
export PATH="/usr/bin:/usr/local/bin:$PATH"

curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt-get update -qq
apt-get install -y -qq nodejs ffmpeg redis-server fonts-sil-padauk fonts-noto-core fonts-noto-cjk fonts-dejavu-core curl

echo "✅ Verified Node: $(node -v) at $(which node)"
echo "✅ Verified NPM: $(npm -v) at $(which npm)"

echo "📦 [2/5] Installing Python dependencies & GPU Voice Cloning (F5-TTS)..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
pip install gradio_client f5-tts -q

echo "🟢 [3/5] Installing Frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo "🌐 [4/5] Setting up Cloudflare Tunnel (cloudflared)..."
if [ ! -f ./cloudflared ]; then
    curl -fsSL -o ./cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x ./cloudflared
fi

echo "=============================================================================="
echo "✅ Environment setup complete! Ready to launch Animaker AI Studio."
echo "=============================================================================="

