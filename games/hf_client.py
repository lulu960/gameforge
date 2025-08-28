
from __future__ import annotations
import os
from typing import List, Tuple
from huggingface_hub import InferenceClient
import dotenv 
from diffusers import DiffusionPipeline
import torch

dotenv.load_dotenv()

HF_TOKEN = os.getenv("HF_TOKEN", None)
HF_TEXT_MODEL = os.getenv("HF_TEXT_MODEL", "HuggingFaceH4/zephyr-7b-beta")
HF_IMAGE_MODEL = os.getenv("HF_IMAGE_MODEL", "runwayml/stable-diffusion-v1-5")

_text_client = None
_image_client = None

def _get_text_client() -> InferenceClient:
    global _text_client
    if _text_client is None:
        _text_client = InferenceClient(model=HF_TEXT_MODEL, token=HF_TOKEN)
    return _text_client

def _get_image_client() -> InferenceClient:
    global _image_client
    if _image_client is None:
        _image_client = InferenceClient(model=HF_IMAGE_MODEL, token=HF_TOKEN)
    return _image_client

SYSTEM_INSTRUCTION = "You are GameForge, an assistant that creates concise, structured game design content in French."

def chat_completion(prompt: str, max_tokens: int = 600) -> str:
    client = _get_text_client()
    print(f"[HF LOG] chat_completion called with prompt: {prompt}")
    try:
        messages = [
            {"role": "system", "content": SYSTEM_INSTRUCTION},
            {"role": "user", "content": prompt},
        ]
        resp = client.chat.completions.create(
            model=HF_TEXT_MODEL,
            messages=messages,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        result = resp.choices[0].message.content.strip()
        print(f"[HF LOG] chat_completion result: {result}")
        return result
    except Exception:
        print(f"[HF LOG] chat_completion failed, fallback to text_generation.")
        try:
            gen = client.text_generation(
                f"{SYSTEM_INSTRUCTION}\nUtilisateur: {prompt}\nAssistant:",
                max_new_tokens=max_tokens,
                temperature=0.7,
            )
            print(f"[HF LOG] text_generation result: {gen.strip()}")
            return gen.strip()
        except Exception as e:
            print(f"[HF LOG] Hugging Face error: {e}")
            return f"[Erreur Hugging Face] {e}"

def txt2img(prompt: str, width: int = 768, height: int = 512) -> bytes:
    print(f"[HF LOG] txt2img called with prompt: {prompt}, size: {width}x{height}")
    try:
        model_id = HF_IMAGE_MODEL
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[HF LOG] Diffusers device used: {device}")
        if device == "cuda":
                pipe = DiffusionPipeline.from_pretrained(model_id, torch_dtype=torch.float16)
        else:
                pipe = DiffusionPipeline.from_pretrained(model_id)
        pipe = pipe.to(device)
        image = pipe(prompt, height=height, width=width).images[0]
        import io
        buf = io.BytesIO()
        image.save(buf, format="PNG")
        print(f"[HF LOG] txt2img image generated successfully.")
        return buf.getvalue()
    except Exception as e:
        import traceback
        print(f"[HF LOG] txt2img error: {e}")
        traceback.print_exc()
        return b""
