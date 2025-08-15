from datasets import load_dataset


dataset = load_dataset("Ekinezya2025/ilac-soru-cevap")
dataset=dataset["train"]
from unsloth import FastLanguageModel
from transformers import TextStreamer
import torch
alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
Read the medical information and provide a clear, simplified, and accurate answer to the question so that a non-medical person can understand it. If safety warnings or important usage instructions are relevant, include them clearly.

### Input:
{}

### Response:
"""

max_seq_length = 512
dtype = "float16"
load_in_4bit = True

torch.cuda.empty_cache()

model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="Ekinezya2025/LlamaModel",
    max_seq_length=max_seq_length,
    dtype=dtype,
    load_in_4bit=load_in_4bit,
)
FastLanguageModel.for_inference(model)
import json, random, csv, os
from statistics import mean
from tqdm.auto import tqdm


def compare_on_dataset_1k(dataset, model, tokenizer, alpaca_prompt):

    results = []
    from rouge_score import rouge_scorer
    from sentence_transformers import util

    scorer = rouge_scorer.RougeScorer(['rouge1','rouge2','rougeL'], use_stemmer=True)

    for i in tqdm(range(min(1000, len(dataset))), desc="Evaluating"):
        question = dataset[i]["question"]
        real_answer = dataset[i]["answer"]

        model_answer = generate_answer(question, model, tokenizer, alpaca_prompt)


        scores = scorer.score(real_answer, model_answer)


        emb = embedder.encode([real_answer, model_answer], convert_to_tensor=True, normalize_embeddings=True)
        semantic_sim = util.cos_sim(emb[0], emb[1]).item()

        results.append({
            "idx": i,
            "question": question,
            "real_answer": real_answer,
            "model_answer": model_answer,
            "rouge1": scores["rouge1"].fmeasure,
            "rouge2": scores["rouge2"].fmeasure,
            "rougeL": scores["rougeL"].fmeasure,
            "semantic_similarity": semantic_sim
        })
    return results


results = compare_on_dataset_1k(dataset, model, tokenizer, alpaca_prompt)


avg_r1 = mean(r["rouge1"] for r in results)
avg_r2 = mean(r["rouge2"] for r in results)
avg_rL = mean(r["rougeL"] for r in results)
avg_sem = mean(r["semantic_similarity"] for r in results)

print(f"\nAverages on {len(results)} examples:")
print(f"  ROUGE-1 F1: {avg_r1:.4f}")
print(f"  ROUGE-2 F1: {avg_r2:.4f}")
print(f"  ROUGE-L F1: {avg_rL:.4f}")
print(f"  Semantic Cosine: {avg_sem:.4f}")