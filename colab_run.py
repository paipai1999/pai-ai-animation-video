"""
Animaker AI - Google Colab Orchestrator & Launcher
Handles starting Redis, FastAPI Backend, Next.js Frontend, and Cloudflare Tunnel in Google Colab.
"""

import os
import sys
import time
import subprocess
import urllib.request
import re


def print_banner():
    print("=" * 70)
    print("  ✨ ANIMAKER AI - GOOGLE COLAB LAUNCHER ✨")
    print("  Fullstack AI Video-to-Animation Remake Studio")
    print("=" * 70)


def setup_cloudflared():
    cf_path = "./cloudflared"
    if not os.path.exists(cf_path):
        print("🌐 Downloading Cloudflare Tunnel (cloudflared)...")
        url = "https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64"
        urllib.request.urlretrieve(url, cf_path)
        os.chmod(cf_path, 0o755)
        print("✅ Cloudflared downloaded successfully.")
    return cf_path


def start_redis():
    try:
        subprocess.Popen(["redis-server", "--daemonize", "yes"])
        print("✅ Redis Server started in background.")
    except Exception as e:
        print(f"ℹ️ Redis daemon notice: {e} (FastAPI BackgroundTasks fallback will be used if needed)")


def check_gpu_hardware():
    """Detects and reports GPU hardware, CUDA capability, and NVENC support."""
    try:
        import torch
        if torch.cuda.is_available():
            gpu_name = torch.cuda.get_device_name(0)
            total_vram_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
            torch.backends.cudnn.benchmark = True
            print(f"🚀 [GPU Hardware Detected]: {gpu_name} ({total_vram_gb:.1f} GB VRAM)")
            print("⚡ [Hardware Acceleration]: CUDA FP16 & NVENC Video Encoding Active")
        else:
            print("ℹ️ [Hardware Notice]: CPU execution mode")
    except Exception as e:
        print(f"ℹ️ GPU detection notice: {e}")


def wait_for_service(url: str, service_name: str, max_wait_sec: int = 45) -> bool:
    """Polls a URL until it responds with HTTP 200 or reachable status."""
    print(f"⏳ Waiting for {service_name} to be ready at {url}...")
    start = time.time()
    while time.time() - start < max_wait_sec:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "HealthCheck/1.0"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status < 500:
                    print(f"✅ {service_name} is UP and healthy!")
                    return True
        except Exception:
            pass
        time.sleep(2)
    print(f"⚠️ {service_name} took longer than expected to report ready.")
    return False


def start_services(gemini_api_key: str = ""):
    print_banner()
    check_gpu_hardware()

    if gemini_api_key:
        os.environ["GEMINI_API_KEY"] = gemini_api_key.strip()
        with open(".env", "w", encoding="utf-8") as f:
            f.write(f"GEMINI_API_KEY={gemini_api_key.strip()}\n")
            f.write("DEFAULT_GENERATOR=pollinations\n")
            f.write("DEFAULT_VOICE=en-US-ChristopherNeural\n")
            f.write('BACKEND_CORS_ORIGINS=["*"]\n')
        print("🔑 GEMINI_API_KEY configured.")

    start_redis()

    print("⚙️ Starting Celery Task Worker...")
    env = os.environ.copy()
    env["PYTHONPATH"] = "."
    celery_log = open("celery.log", "w", encoding="utf-8")
    celery_proc = subprocess.Popen(
        [sys.executable, "-m", "celery", "-A", "backend.app.core.celery_app", "worker", "--loglevel=info", "--pool=threads", "-c", "4"],
        env=env,
        stdout=celery_log,
        stderr=subprocess.STDOUT
    )

    print("🚀 Starting FastAPI Backend on Port 8000...")
    backend_log = open("backend.log", "w", encoding="utf-8")
    backend_proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"],
        env=env,
        stdout=backend_log,
        stderr=subprocess.STDOUT
    )

    # Wait for Backend to become ready
    wait_for_service("http://127.0.0.1:8000/api/health", "FastAPI Backend", max_wait_sec=20)

    print("🎨 Starting Next.js Frontend on Port 3000...")
    frontend_dir = os.path.join(os.getcwd(), "frontend")
    frontend_log = open("frontend.log", "w", encoding="utf-8")

    # Purge legacy /tools/node from Colab to prevent node:path error
    if os.path.exists("/tools/node"):
        try:
            import shutil
            shutil.rmtree("/tools/node", ignore_errors=True)
        except Exception:
            pass

    front_env = os.environ.copy()
    front_env["PATH"] = f"/usr/bin:/usr/local/bin:{front_env.get('PATH', '')}"

    # Check if .next build exists, use start for instant launch; otherwise dev
    has_build = os.path.exists(os.path.join(frontend_dir, ".next"))
    start_cmd = ["npm", "run", "start", "--", "-p", "3000", "-H", "0.0.0.0"] if has_build else ["npm", "run", "dev", "--", "-p", "3000", "-H", "0.0.0.0"]

    frontend_proc = subprocess.Popen(
        start_cmd,
        cwd=frontend_dir,
        env=front_env,
        stdout=frontend_log,
        stderr=subprocess.STDOUT
    )

    # Wait for Frontend to become ready
    wait_for_service("http://127.0.0.1:3000", "Next.js Frontend", max_wait_sec=40)

    cf_bin = setup_cloudflared()
    print("\n" + "=" * 70)
    print("  🌐 GENERATING SECURE PUBLIC HTTPS URL VIA CLOUDFLARE TUNNEL...")
    print("=" * 70)

    tunnel_cmd = [cf_bin, "tunnel", "--url", "http://127.0.0.1:3000"]
    tunnel_proc = subprocess.Popen(
        tunnel_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    public_url = None
    start_time = time.time()

    while time.time() - start_time < 35:
        line = tunnel_proc.stdout.readline()
        if not line:
            continue
        match = re.search(r"https://[a-zA-Z0-9-]+\.trycloudflare\.com", line)
        if match:
            public_url = match.group(0)
            break

    if public_url:
        print("\n" + "🎉" * 25)
        print("  🌟 YOUR ANIMAKER AI STUDIO IS LIVE & FULLY READY! 🌟")
        print(f"  👉 PUBLIC WEB UI URL:  {public_url}")
        print("🎉" * 25 + "\n")
        print("💡 You can open this link in any browser on PC, Mac, iPad, or Mobile phone!")
        print("💡 Keep this Colab cell running to keep the Studio online.\n")
    else:
        print("ℹ️ Tunnel starting in background. Check outputs or local port 3000.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Stopping services...")
        backend_proc.terminate()
        frontend_proc.terminate()
        celery_proc.terminate()
        tunnel_proc.terminate()
        print("Done.")


if __name__ == "__main__":
    key = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GEMINI_API_KEY", "")
    start_services(key)


