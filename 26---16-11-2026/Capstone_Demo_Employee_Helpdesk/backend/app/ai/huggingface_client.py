
from functools import lru_cache

MODEL_PATH = "models/qwen2.5-3b-instruct"
MODEL_NAME = "Qwen/Qwen2.5-3B-Instruct"


@lru_cache(maxsize=1)
def get_llm():
    from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline
    from langchain_huggingface import HuggingFacePipeline

    print("Loading Hugging Face model...")

    tokenizer = AutoTokenizer.from_pretrained(
        MODEL_PATH
    )

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_PATH,
        torch_dtype="auto",
        device_map="auto"
    )

    hf_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        max_new_tokens=512,
        do_sample=False,
        return_full_text=False
    )

    llm = HuggingFacePipeline(
        pipeline=hf_pipeline
    )

    print("Model loaded successfully!")

    return llm
