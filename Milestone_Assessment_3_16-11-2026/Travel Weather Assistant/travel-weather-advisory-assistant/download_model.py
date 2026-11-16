from pathlib import Path
from huggingface_hub import snapshot_download
ROOT=Path(__file__).resolve().parent
MODEL_ID="Qwen/Qwen2.5-0.5B-Instruct"
MODEL_DIR=ROOT/"Models"/"Qwen2.5-0.5B-Instruct"
print("Downloading: ",MODEL_ID)
snapshot_download(repo_id=MODEL_ID,local_dir=str(MODEL_DIR))
print("Model download successfully and saved at: ",MODEL_DIR)