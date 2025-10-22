from builtins import callable
from transformers import DistilBertTokenizer, DistilBertForSequenceClassification, TrainingArguments, Trainer
import numpy as np
import torch
from transformers.modeling_utils import SpecificPreTrainedModelType
import os
from backend.filetype import FileType as ft
from datasets import Dataset
import pandas as pd
from pathlib import Path

def __load_datasets() -> Dataset:
    folder_path = Path("datasets")
    csv_files = list(folder_path.glob("*.csv"))

    # Liste für alle DataFrames
    df_list = []

    for csv_file in csv_files:
        df = pd.read_csv(csv_file, delimiter=';', encoding='utf-8')
        df_list.append(df)

    # Alle DataFrames zusammenführen
    combined_df = pd.concat(df_list, ignore_index=True)

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
    train_test = tokenized_chunked_dataset.train_test_split(test_size=0.2)
    training_args = TrainingArguments(
        output_dir=path + 'results',
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
    trainer.train()
    trainer.save_model(path + 'trained_model')
    tokenizer.save_pretrained(path + 'trained_model')

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
    print(probs)
    avg_probs = np.mean(probs, axis=0)  # Durchschnitt über Chunks
    pred_label = np.argmax(avg_probs)
    return pred_label, avg_probs


path = './ml_results/'
tokenizer: DistilBertTokenizer
model: SpecificPreTrainedModelType

# api ##############################################
def prepare_transformer():
    global tokenizer
    global model

    if not os.path.isdir(path):
        tokenizer = DistilBertTokenizer.from_pretrained('distilbert-base-uncased')
        model = DistilBertForSequenceClassification.from_pretrained('distilbert-base-uncased', num_labels=4)
        __train_model_with_example_data()
    else:
        tokenizer = DistilBertTokenizer.from_pretrained(path + 'trained_model')
        model = DistilBertForSequenceClassification.from_pretrained(path + 'trained_model', num_labels=4)

    model.eval()

# api #############
def make_prediction(text: str) -> tuple[str, list]:
    """Make a prediction. The model has to be prepared before"""
    label, probs = __predict(text=text)
    return str(ft(label).name), probs

# api #############
def predict(text: str) -> tuple[str, list]:
    """Prepare the model and make a prediction"""
    prepare_transformer()
    return make_prediction(text)

