from builtins import callable

from numpy import signedinteger
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import torch
from transformers.modeling_utils import SpecificPreTrainedModelType
import os
from backend.enums.FileType import FileType as ft
from datasets import Dataset
import pandas as pd
from pathlib import Path
from huggingface_hub import HfApi
from synth_datasets.dataset_central_generator import generate_datasets


def __load_datasets() -> Dataset:
    folder_path = Path("../synth_datasets")
    csv_files = list(folder_path.glob("*.csv"))

    # Liste für alle DataFrames
    df_list = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
        df_list.append(df)

    # Alle DataFrames zusammenführen
    combined_df = pd.concat(df_list, ignore_index=True)
    print(f"Loaded {len(combined_df)} rows")

    return Dataset.from_pandas(combined_df.reset_index(drop=True))

# Tokenisierung und Chunking #####################
def __chunk_text(txt: str, chunk_size=512):
    tokens = tokenizer.tokenize(txt)
    chunks = []
    for i in range(0, len(tokens), chunk_size):
        chunk_tokens = tokens[i:i + chunk_size]
        chunks.append(tokenizer.convert_tokens_to_string(chunk_tokens))
    return chunks[:3]  # max. 3 Chunks

# Dataset chunken #################
def __chunk_dataset(raw_dataset: Dataset):
    data = {'text': [], 'label': []}
    for row in raw_dataset:
        text = row['text']
        label = row['label']
        chunks = __chunk_text(text)
        for chunk in chunks:
            data['text'].append(chunk)
            data['label'].append(label)

    return Dataset.from_dict(data)

# Tokenisierung fürs Training #############
def __tokenize_lambda(data: dict):
    return tokenizer(data['text'], padding='max_length', truncation=True, max_length=512)

def __tokenize_dataset(chunked_dataset: Dataset, tokenize_function: callable):
    return chunked_dataset.map(tokenize_function, batched=True)

# Modell laden und Trainer konfigurieren ###########
def __train(tokenized_chunked_dataset: Dataset):
    global model
    global tokenizer
    train_test = tokenized_chunked_dataset.train_test_split(test_size=0.2)
    training_args = TrainingArguments(
        output_dir=path + 'output',
        do_eval=True,
        learning_rate=2e-5,
        per_device_train_batch_size=8,
        per_device_eval_batch_size=8,
        num_train_epochs=3,
        weight_decay=0.01,
        save_total_limit=2
    )

    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=train_test['train'],
        eval_dataset=train_test['test'],
        tokenizer=tokenizer
    )
    try:
        print(f"GPU: {torch.cuda.is_available()}")
        print(f"GPU: {torch.cuda.current_device()}")
    except Exception as _:
        print("Training with CPU. Please enable cuda support for acceleration and install the requirements_nvidia_cuda_support.txt via \n pip install --upgrade -r requirements_nvidia_cuda_support.txt")

    trainer.train()
    __save_model_to_hugging_face()

def __save_model_to_hugging_face():
    global model
    global tokenizer
    global repo_id

    model.push_to_hub(repo_id=repo_id, commit_message="Upload of distilBERT model")
    tokenizer.push_to_hub(repo_id=repo_id)
    print(f"Saved model and tokenizer to hugging face repo \"{repo_id}\"")

def __train_model_with_example_data():
    ex_dataset = __load_datasets()
    chunked_dataset = __chunk_dataset(ex_dataset)
    tokenized_chunked_dataset = __tokenize_dataset(chunked_dataset, __tokenize_lambda)
    __train(tokenized_chunked_dataset=tokenized_chunked_dataset)

# Vorhersage #########
def __predict(text: str):
    chunks = __chunk_text(text)
    inputs = tokenizer(chunks, padding=True, truncation=True, max_length=512, return_tensors='pt')
    outputs = model(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=-1).detach().cpu().numpy()
    avg_probs = np.mean(probs, axis=0)  # Durchschnitt über Chunks
    pred_label = np.argmax(avg_probs)
    return pred_label, avg_probs


path = '../ml_results/'
trainer_path = path + 'distilbert_trained'
data_path = '../synth_datasets'
repo_id = 'SumoOW/distilbert-base-uncased'
tokenizer: DistilBertTokenizer
model: SpecificPreTrainedModelType

# api ##############################################
def prepare_model():
    global tokenizer
    global model

    data_rows = 80000
    if __is_hf_model_available():
        print(f"Loading pre-trained model from hugging face repo \"{repo_id}\"")
        tokenizer = DistilBertTokenizer.from_pretrained(repo_id)
        model = DistilBertForSequenceClassification.from_pretrained(repo_id, num_labels=4)
    else:
        print(f"No pre-trained hugging face model from repo \"{repo_id}\" found")
        if not __is_datasets_created():
            print(f"No Datasets found. Creating {data_rows} data rows")
            generate_datasets(rows_total=data_rows)
            print("Created data")

        print("Beginning training with data")
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=4)
        __train_model_with_example_data()

    model.eval()
    print("Preperation Done. Model in eval mode")

def __is_datasets_created() -> bool:
    return sum(fname.endswith('.csv') for fname in os.listdir(data_path)) == 4

def __is_hf_model_available() -> bool:
    global repo_id
    hf_api = HfApi()

    try:
        repo_info = hf_api.repo_info(repo_id)
        print(f"Model \"{repo_id}\" is available. Last modified: {repo_info.last_modified}")
        return True
    except Exception as e:
        return False

# api #############
def predict(text: str) -> tuple[str, float]:
    """Make a prediction. The model has to be prepared before"""
    label, probs = __predict(text=text)
    t = str(ft(label).name)
    prob_best = float(probs[label])
    prob_second = float(probs[label])
    return t, prob

# api #############
def prepare_and_predict(text: str) -> tuple[str, float]:
    """Prepare the model and make a prediction"""
    prepare_model()
    return predict(text)

