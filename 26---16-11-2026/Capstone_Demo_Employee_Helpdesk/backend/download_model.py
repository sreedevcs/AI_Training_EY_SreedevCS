
from huggingface_hub import snapshot_download

model_id = "Qwen/Qwen2.5-3B-Instruct"

download_path = snapshot_download(
    repo_id=model_id,
    local_dir="./models/qwen2.5-3b-instruct"
)

print("Model downloaded successfully!")
print("Location:", download_path)
