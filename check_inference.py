import os
import sys

# Display inference.py executable status and environment setup
print("=== Inference.py Executable Verification ===")
print()

inf_path = r'D:\debugtrace-env-new\inference.py'
print(f"File path: {inf_path}")
print(f"File exists: {os.path.isfile(inf_path)}")
print(f"File readable: {os.access(inf_path, os.R_OK)}")
print(f"File executable: {os.access(inf_path, os.X_OK)}")
print()

# Check file permissions
import stat
st = os.stat(inf_path)
print(f"File permissions: {oct(st.st_mode)}")
print()

# Display key environment variables needed
print("=== Required Environment Variables ===")
print(f"HF_TOKEN set: {bool(os.getenv('HF_TOKEN'))}")
print(f"API_BASE_URL: {os.getenv('API_BASE_URL', 'https://openrouter.ai/api/v1')}")
print(f"MODEL_NAME: {os.getenv('MODEL_NAME', 'nvidia/nemotron-3-super-120b-a12b:free')}")
print()

# Display what ENV_BASE_URL should be for Space
print("=== Endpoint Configuration ===")
print(f"Current ENV_BASE_URL: {os.getenv('ENV_BASE_URL', 'http://localhost:7860')}")
print(f"For live Space, use:  https://umesh-tirumani-debugtrace-env.hf.space")
print()

# Show the inference.py shebang
print("=== Script Header ===")
with open(inf_path, 'r') as f:
    for i, line in enumerate(f):
        if i < 3:
            print(line.rstrip())
        else:
            break
