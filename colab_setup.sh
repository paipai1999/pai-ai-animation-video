#!/usr/bin/env bash
# ==============================================================================
# Animaker AI - Google Colab Environment Setup Script
# ==============================================================================
set -e

echo "🚀 [1/4] Updating Linux packages & installing FFmpeg, Redis..."
apt-get update -qq
apt-get install -y -qq nodejs npm ffmpeg redis-server fonts-noto-cjk fonts-dejavu-core curl

echo "📦 [2/4] Installing Python dependencies & GPU Voice Cloning (F5-TTS)..."
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
pip install gradio_client f5-tts -q


echo "🟢 [3/4] Installing Frontend dependencies..."
cd frontend
npm install --silent
cd ..

echo "🌐 [4/4] Setting up Cloudflare Tunnel (cloudflared)..."
if [ ! -f ./cloudflared ]; then
    curl -fsSL -o ./cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
    chmod +x ./cloudflared
fi

echo "=============================================================================="
echo "✅ Environment setup complete! Ready to launch Animaker AI Studio."
echo "=============================================================================="
