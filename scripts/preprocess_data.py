import os

import pandas as pd
import numpy as np
from BERT_converter import BertConverter, BertSentenceConverter
from reduce_function import Reducer
import json
import gzip
import matplotlib.pyplot as plt


def read_data(data_dir: str):
    pd_dict = {
        "labels": [],
        "text": [],
        "special_tokens": []
    }
    df = pd.read_csv(data_dir, sep=';').T
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)
    df_filtered = df.loc[df['Szenario'].isin(["Web(Patrick)", "VR(Patrick)"])]
    print(f"Number of rows: {df_filtered.shape[0]} and number of columns: {df_filtered.shape[1]}")
    for index, row in df_filtered.iterrows():
        label_i = row["Szenario"]
        text_i = row["Path Description"]
        if not isinstance(text_i, str):
            continue
        text_i = text_i.split("->")
        for sentence_i in text_i:
            if sentence_i == "":
                continue
            pd_dict["labels"].append(label_i)
            pd_dict["text"].append(sentence_i)
            pd_dict["special_tokens"].append("")
    return pd_dict


def create_embeddings(data: dict):
    converter = BertSentenceConverter("distiluse-base-multilingual-cased-v2", "cuda:0cona")
    embeddings = converter.encode_to_vec(data["text"])
    data["embeddings"] = embeddings
    return data


def reduce_dimensions(data: dict):
    reducer = Reducer("PACMAP", 2, 42)
    embeddings = reducer.reducer(data["embeddings"], True)
    data["reduced_embeddings"] = embeddings
    return data


def run_pipeline(data_dir: str, output_dir: str):
    print("Reading data")
    data = read_data(data_dir)
    if os.path.exists(f"{output_dir}/Embeddings.json.gz"):
        with gzip.open(f"{output_dir}/Embeddings.json.gz", "rt", encoding="UTF-8") as json_file:
            data = json.load(json_file)
    else:
        print("Creating embeddings")
        data = create_embeddings(data)
        with gzip.open(f"{output_dir}/Embeddings.json.gz", "wt", encoding="UTF-8") as json_file:
            json.dump(data, json_file, indent=2)
    if os.path.exists(f"{output_dir}/Data.json.gz"):
        with gzip.open(f"{output_dir}/Data.json.gz", "rt", encoding="UTF-8") as json_file:
            data = json.load(json_file)
    else:
        print("Reducing dimensions")
        data = reduce_dimensions(data)
        print("Saving data")
        out_dir = f"{output_dir}/Data.json.gz"
        os.makedirs(os.path.dirname(out_dir), exist_ok=True)
        with gzip.open(out_dir, "wt", encoding="UTF-8") as json_file:
            json.dump(data, json_file, indent=2)
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.scatter(data["reduced_embeddings"][:, 0], data["reduced_embeddings"][:, 1], cmap="Spectral", c=data["labels"])
    #Legend
    # handles, labels = ax.get_legend_handles_labels()
    # unique_labels = list(set(data["labels"]))
    # unique_labels.sort()
    # ax.legend(handles, unique_labels, title="Szenario")
    plt.savefig(f"{output_dir}/plot.png")


if __name__ == '__main__':
    run_pipeline("Data.csv", "/storage/projects/bagci/data/NewsInTimeAndSpace")
