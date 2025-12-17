#!/usr/bin/env python3
"""
Chatterbox-TTS Interactive Installer v7
Supports Windows and Linux with menu-driven setup
"""
import os
import sys
import platform
import shutil
import subprocess
import urllib.request
from pathlib import Path

# ============================================================================
# Configuration
# ============================================================================

VENV_NAME = "Chatterbox_TTS"
MODEL_DIR = "Model"

# Model file definitions
ORIGINAL_FILES = [
    "https://huggingface.co/ResembleAI/chatterbox/resolve/main/t3_cfg.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox/resolve/main/s3gen.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox/resolve/main/tokenizer.json?download=true",
    "https://huggingface.co/ResembleAI/chatterbox/resolve/main/ve.safetensors?download=true",
]

TURBO_FILES = [
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/s3gen.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/conds.pt?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/added_tokens.json?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/s3gen_meanflow.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/special_tokens_map.json?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/t3_turbo_v1.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/t3_turbo_v1.yaml?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/tokenizer_config.json?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/ve.safetensors?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/vocab.json?download=true",
    "https://huggingface.co/ResembleAI/chatterbox-turbo/resolve/main/merges.txt?download=true",
]

ORIGINAL_EXPECTED = ["t3_cfg.safetensors", "s3gen.safetensors", "tokenizer.json", "ve.safetensors"]
TURBO_EXPECTED = [
    "added_tokens.json", "conds.pt", "merges.txt", "s3gen.safetensors",
    "s3gen_meanflow.safetensors", "special_tokens_map.json", "t3_turbo_v1.safetensors",
    "t3_turbo_v1.yaml", "tokenizer_config.json", "ve.safetensors", "vocab.json"
]

# ============================================================================
# Utility Functions
# ============================================================================

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if platform.system().lower() == 'windows' else 'clear')

def print_header(text):
    """Print a formatted header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_warning(text):
    """Print a warning message."""
    print(f"⚠️  {text}")

def print_success(text):
    """Print a success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print an error message."""
    print(f"✗ {text}")

def run(cmd, check=True, capture=False):
    """Run shell command."""
    if capture:
        return subprocess.run(cmd, shell=isinstance(cmd, str), check=check,
                              capture_output=True, text=True).stdout.strip()
    subprocess.run(cmd, shell=isinstance(cmd, str), check=check)

def pip_install(*args):
    """Install packages with pip."""
    if PIP_EXE.exists():
        cmd = [str(PIP_EXE), "install", "--upgrade"]
    else:
        cmd = [str(PYTHON_EXE), "-m", "pip", "install", "--upgrade"]
    
    cmd.extend(args)
    
    try:
        run(cmd)
    except subprocess.CalledProcessError as e:
        print_warning(f"Install failed: {e}")
        print_warning("Retrying once...")
        run(cmd)

def download_file(url, dest: Path):
    """Download file with progress indication."""
    filename = url.split('/')[-1].split('?')[0]
    print(f"📥 Downloading {filename}...")
    try:
        urllib.request.urlretrieve(url, dest)
        print_success(f"Downloaded {filename}")
    except Exception as e:
        print_error(f"Failed to download {filename}: {e}")
        raise

def get_user_choice(prompt, options):
    """Get validated user input."""
    while True:
        print(prompt)
        for i, option in enumerate(options, 1):
            print(f"{i}. {option}")
        
        try:
            choice = input("\nEnter your choice (number): ").strip()
            choice_num = int(choice)
            if 1 <= choice_num <= len(options):
                return choice_num
            else:
                print_error(f"Please enter a number between 1 and {len(options)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nInstallation cancelled.")
            sys.exit(0)

def validate_user_supplied_files(folder_path, expected_files):
    """Validate that user-supplied folder contains required files."""
    folder = Path(folder_path)
    if not folder.exists() or not folder.is_dir():
        return False, "Folder does not exist or is not a directory"
    
    missing_files = []
    for file in expected_files:
        if not (folder / file).exists():
            missing_files.append(file)
    
    if missing_files:
        return False, f"Missing files: {', '.join(missing_files)}"
    
    return True, "All files present"

def python_tag():
    """Return cp310/cp311/cp312/cp313 based on running interpreter."""
    v = sys.version_info
    return f"cp{v.major}{v.minor}"

# ============================================================================
# Main Installation Flow
# ============================================================================

def main():
    global PYTHON_EXE, PIP_EXE, ACTIVATE, VENV_DIR
    
    # Detect OS
    OS = platform.system().lower()
    if OS not in ["windows", "linux"]:
        print_error(f"Unsupported operating system: {OS}")
        print("This installer only supports Windows and Linux")
        sys.exit(1)
    
    clear_screen()
    print_header("Chatterbox-TTS Installer")
    print(f"Detected OS: {OS.capitalize()}\n")
    
    # ========================================================================
    # Step 1: Model Selection
    # ========================================================================
    print_header("Step 1: Model Selection")
    print("Welcome! Ready to Install Chatterbox? Start by entering an option below:\n")
    print("Available Models:\n")
    
    model_choice = get_user_choice(
        "",
        [
            "Chatterbox (Original): Zero-shot cloning, Multiple Languages, Slower",
            "Chatterbox (Turbo): Paralinguistic Tags ([laugh]), Lower Compute and VRAM, Faster, May reduce quality",
            "Chatterbox (Original, User Supplied): Same as Option 1, but you will supply the model files",
            "Chatterbox (Turbo, User Supplied): Same as Option 2, but you will supply files"
        ]
    )
    
    # Determine model type and download method
    is_turbo = model_choice in [2, 4]
    is_user_supplied = model_choice in [3, 4]
    model_type = "Turbo" if is_turbo else "Original"
    
    user_model_path = None
    if is_user_supplied:
        print(f"\nYou selected User Supplied {model_type} model.")
        expected_files = TURBO_EXPECTED if is_turbo else ORIGINAL_EXPECTED
        print("\nRequired files:")
        for f in expected_files:
            print(f"  - {f}")
        
        while True:
            folder_path = input("\nEnter the full path to your model folder: ").strip()
            if folder_path.startswith('"') and folder_path.endswith('"'):
                folder_path = folder_path[1:-1]
            
            valid, message = validate_user_supplied_files(folder_path, expected_files)
            if valid:
                print_success(message)
                user_model_path = Path(folder_path)
                break
            else:
                print_error(message)
                retry = input("Try again? (y/n): ").strip().lower()
                if retry != 'y':
                    print("Installation cancelled.")
                    sys.exit(0)
    else:
        print(f"\nYou selected {model_type} model (download from repository).")
        print_warning("These files are large and may incur data charges if you don't have an unlimited plan.")
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm != 'y':
            print("Installation cancelled.")
            sys.exit(0)
    
    # ========================================================================
    # Step 2: Backend Selection
    # ========================================================================
    print_header("Step 2: Backend Selection")
    print("Great! Now, you'll need to choose your backend:\n")
    
    backend_options = [
        "CPU: Choose this if you do not have a GPU or want to only use your CPU, CPU generation may be very slow on older/low power CPUs",
        "AMD (ROCm): Linux Only, AMD RX 6000 Series and newer",
        "Nvidia (CUDA): RTX 30 and newer only"
    ]
    
    backend_choice = get_user_choice("", backend_options)
    
    # Validate backend choice
    if backend_choice == 2 and OS != "linux":
        print_error("AMD ROCm is only supported on Linux!")
        print("Please restart and choose a different backend.")
        sys.exit(1)
    
    backend_name = ["CPU", "AMD (ROCm)", "Nvidia (CUDA)"][backend_choice - 1]
    print(f"\nYou selected: {backend_name}")
    
    # ========================================================================
    # Step 3: Virtual Environment Setup
    # ========================================================================
    print_header("Step 3: Environment Setup")
    
    VENV_DIR = Path(VENV_NAME).resolve()
    if OS == "windows":
        PYTHON_EXE = VENV_DIR / "Scripts" / "python.exe"
        PIP_EXE = VENV_DIR / "Scripts" / "pip.exe"
        ACTIVATE = VENV_DIR / "Scripts" / "activate.ps1"
    else:
        PYTHON_EXE = VENV_DIR / "bin" / "python"
        PIP_EXE = VENV_DIR / "bin" / "pip"
        ACTIVATE = VENV_DIR / "bin" / "activate"
    
    # Create venv if missing
    if not VENV_DIR.exists():
        print("Creating virtual environment...")
        run([sys.executable, "-m", "venv", str(VENV_DIR)])
        print_success("Virtual environment created")
    else:
        print_success("Virtual environment already exists")
    
    # Re-exec inside venv if needed
    if Path(sys.executable).resolve() != PYTHON_EXE.resolve():
        print("Activating virtual environment...")
        os.execv(str(PYTHON_EXE), [str(PYTHON_EXE), __file__])
    
    # Ensure pip exists
    if not PIP_EXE.exists():
        print("Ensuring pip is available...")
        run([str(PYTHON_EXE), "-m", "ensurepip", "--upgrade"])
    
    # ========================================================================
    # Step 4: PyTorch Installation
    # ========================================================================
    print_header("Step 4: Installing PyTorch")
    
    tag = python_tag()
    
    if backend_choice == 1:  # CPU
        print("Installing CPU-only PyTorch...")
        pip_install("torch==2.6.0", "torchvision==0.21.0", "torchaudio==2.6.0",
                    "--index-url", "https://download.pytorch.org/whl/cpu")
    
    elif backend_choice == 2:  # AMD ROCm
        print("Installing ROCm PyTorch...")
        pip_install("torch==2.6.0", "torchvision==0.21.0", "torchaudio==2.6.0",
                    "--index-url", "https://download.pytorch.org/whl/rocm6.2.4")
    
    elif backend_choice == 3:  # Nvidia CUDA
        print("Installing CUDA PyTorch...")
        pip_install("torch==2.6.0", "torchvision==0.21.0", "torchaudio==2.6.0",
                    "--index-url", "https://download.pytorch.org/whl/cu124")
        
        # Install flash-attention
        print("\nInstalling flash-attention for RTX 30+ series...")
        if OS == "linux":
            flash_url = (f"https://github.com/mjun0812/flash-attention-prebuild-wheels/"
                        f"releases/download/v0.3.18/flash_attn-2.7.4+cu124torch2.6-"
                        f"{tag}-{tag}-linux_x86_64.whl")
        else:  # Windows
            flash_url = (f"https://github.com/mjun0812/flash-attention-prebuild-wheels/"
                        f"releases/download/v0.3.9/flash_attn-2.7.4+cu124torch2.6-"
                        f"{tag}-{tag}-win_amd64.whl")
        
        try:
            pip_install(flash_url)
            print_success("flash-attention installed")
        except Exception as e:
            print_warning(f"flash-attention installation failed: {e}")
            print_warning("Continuing without flash-attention (may affect performance)")
    
    # ========================================================================
    # Step 5: Chatterbox-TTS Dependencies
    # ========================================================================
    print_header("Step 5: Installing Chatterbox-TTS Dependencies")
    
    print("Installing chatterbox-tts (without dependencies)...")
    pip_install("--no-deps", "chatterbox-tts")
    
    print("\nInstalling core dependencies...")
    dependencies = [
        "numpy>=1.24.0,<1.26.0",
        "librosa==0.11.0",
        "safetensors==0.5.3",
        "huggingface_hub>=0.23.2,<1.0",  # Must install before transformers
        "transformers==4.46.3",
        "diffusers==0.29.0",
        "einops",
        "s3tokenizer",
        "conformer==0.3.2",
        "resemble-perth==1.0.1",
        "pykakasi==2.3.0",
        "gradio==5.44.1",
        "soundfile>=0.12.1",
        "audioread>=2.1.9",
        "omegaconf>=2.3.0",  # Required by chatterbox but not declared
        "pyloudnorm",
        "spacy-pkuseg"
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            pip_install(dep)
        except Exception as e:
            print_warning(f"Failed to install {dep}: {e}")
            print_warning("Continuing with remaining dependencies...")
    
    # ========================================================================
    # Step 6: Model Download/Copy
    # ========================================================================
    print_header("Step 6: Setting Up Model Files")
    
    model_path = Path(MODEL_DIR)
    model_path.mkdir(exist_ok=True)
    
    if is_user_supplied:
        print(f"Copying model files from {user_model_path}...")
        expected_files = TURBO_EXPECTED if is_turbo else ORIGINAL_EXPECTED
        for file in expected_files:
            src = user_model_path / file
            dst = model_path / file
            if src.exists():
                shutil.copy2(src, dst)
                print_success(f"Copied {file}")
        print_success("All model files copied")
    else:
        print("Downloading model files...")
        files_to_download = TURBO_FILES if is_turbo else ORIGINAL_FILES
        for url in files_to_download:
            filename = url.split('/')[-1].split('?')[0]
            dest = model_path / filename
            if not dest.exists():
                download_file(url, dest)
            else:
                print_success(f"{filename} already exists, skipping")
    
    # ========================================================================
    # Step 7: Verification
    # ========================================================================
    print_header("Step 7: Installation Verification")
    
    print("Verifying Python packages...")
    critical_packages = [
        "torch", "torchaudio", "librosa", "safetensors", "transformers",
        "diffusers", "conformer", "s3tokenizer", "resemble_perth", "einops",
        "huggingface_hub", "soundfile", "audioread"
    ]
    
    failed_packages = []
    for pkg in critical_packages:
        try:
            # Use venv's python to check if package is importable
            result = subprocess.run(
                [str(PYTHON_EXE), "-c", f"import {pkg}"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                print_success(pkg)
            else:
                print_error(pkg)
                failed_packages.append(pkg)
        except Exception as e:
            print_error(f"{pkg} (check failed: {e})")
            failed_packages.append(pkg)
    
    if failed_packages:
        print_warning(f"\nSome packages failed to install: {', '.join(failed_packages)}")
        print_warning("You may need to install these manually later.")
    
    # ========================================================================
    # Final Summary
    # ========================================================================
    print_header("Installation Complete!")
    
    if failed_packages:
        print("⚠️  Installation completed with warnings")
        print(f"Failed packages: {', '.join(failed_packages)}\n")
    else:
        print_success("All components installed successfully!\n")
    
    print("Configuration:")
    print(f"  • Model: Chatterbox {model_type}")
    print(f"  • Backend: {backend_name}")
    print(f"  • Model files: {model_path.resolve()}\n")
    
    print("To use Chatterbox-TTS:")
    if OS == "linux":
        print(f"  source {ACTIVATE}")
    else:
        print(f"  {ACTIVATE}")
    print("  python your_script.py\n")
    
    if backend_choice == 1:
        print("Note: Using CPU backend. Use device='cpu' in your scripts.\n")
    
    print("For audio issues, install ffmpeg:")
    if OS == "linux":
        print("  sudo apt-get install ffmpeg")
    else:
        print("  Download from: https://ffmpeg.org/download.html")
    
    print("\n" + "="*70)
    print("  Thank you for installing Chatterbox-TTS!")
    print("="*70 + "\n")

# ============================================================================
# Entry Point
# ============================================================================

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Installation failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)