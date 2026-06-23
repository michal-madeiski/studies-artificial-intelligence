from transformers import pipeline
import torch
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm
import gc


def evaluate_encoder(model_name, label_mapping, texts, true_labels):
    print(f"\n--- INITIALIZING MODEL: {model_name} ---")

    sentiment_pipeline = pipeline(
        "text-classification",
        model=model_name,
        device=0 if torch.cuda.is_available() else -1,
    )

    predictions = []

    for out in tqdm(
        sentiment_pipeline(texts, batch_size=16, truncation=True, max_length=512)
    ):
        predictions.append(out["label"])

    mapped_predictions = [label_mapping.get(pred.lower(), pred) for pred in predictions]

    acc = accuracy_score(true_labels, mapped_predictions)
    f1 = f1_score(true_labels, mapped_predictions, average="weighted")

    print(f"Results -> Accuracy: {acc:.4f} | F1: {f1:.4f}")

    del sentiment_pipeline
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    return acc, f1


shared_mapping = {
    "positive": "__label__meta_plus_m",
    "negative": "__label__meta_minus_m",
    "neutral": "__label__meta_zero",
}

acc_herbert, f1_herbert = evaluate_encoder(
    model_name="Voicelab/herbert-base-cased-sentiment",
    label_mapping=shared_mapping,
    texts=texts,
    true_labels=true_labels,
)

acc_roberta, f1_roberta = evaluate_encoder(
    model_name="cardiffnlp/twitter-xlm-roberta-base-sentiment",
    label_mapping=shared_mapping,
    texts=texts,
    true_labels=true_labels,
)

print("--- MODEL COMPARISON SUMMARY ---")
print(
    f"1. Voicelab/herbert-base-cased-sentiment -> Accuracy: {acc_herbert:.4f} | F1: {f1_herbert:.4f}"
)
print(
    f"2. cardiffnlp/twitter-xlm-roberta-base-sentiment -> Accuracy: {acc_roberta:.4f} | F1: {f1_roberta:.4f}"
)
