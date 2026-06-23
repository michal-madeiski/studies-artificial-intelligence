from datasets import load_dataset
import pandas as pd
import torch
import gc
from transformers import pipeline, AutoModelForCausalLM, AutoTokenizer
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm

dataset = load_dataset("allegro/klej-polemo2-in", split="test")
df = dataset.to_pandas()
df_filtered = df[df["target"] != "__label__meta_amb"].copy()
texts = df_filtered["sentence"].tolist()
true_labels = df_filtered["target"].tolist()

llm_model_name = "Qwen/Qwen2.5-1.5B-Instruct"
print(f"--- INITIALIZING MODEL: {llm_model_name} ---")

tokenizer = AutoTokenizer.from_pretrained(llm_model_name)
model = AutoModelForCausalLM.from_pretrained(
    llm_model_name, torch_dtype=torch.bfloat16, device_map="auto"
)

hf_pipeline = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    temperature=0.1,
    do_sample=True,
    pad_token_id=tokenizer.eos_token_id,
    max_new_tokens=5,
    return_full_text=False,
)

llm = HuggingFacePipeline(pipeline=hf_pipeline)

basic_template = """Classify the text sentiment into one of three classes:
positive, negative, neutral. Respond with exactly ONE word. Do not add any punctuation.
Text: {text}
Class:"""

prompt = PromptTemplate.from_template(basic_template)
llm_chain = prompt | llm

raw_predictions = []

for text in tqdm(texts):
    short_text = " ".join(str(text).split()[:150])
    try:
        result = llm_chain.invoke({"text": short_text})
        raw_predictions.append(result.strip().lower())
    except Exception as e:
        raw_predictions.append("error")

mapped_predictions = []
for pred in raw_predictions:
    if "positive" in pred or "plus" in pred:
        mapped_predictions.append("__label__meta_plus_m")
    elif "negative" in pred or "minus" in pred:
        mapped_predictions.append("__label__meta_minus_m")
    elif "neutral" in pred or "zero" in pred:
        mapped_predictions.append("__label__meta_zero")
    else:
        mapped_predictions.append("__label__meta_zero")

accuracy = accuracy_score(true_labels, mapped_predictions)
f1 = f1_score(true_labels, mapped_predictions, average="weighted")

print("\n--- DECODER-ONLY MODEL RESULTS ---")
print(f"Accuracy: {accuracy:.4f}")
print(f"F1: {f1:.4f}")

del model
del hf_pipeline
del llm
gc.collect()
torch.cuda.empty_cache()
