import os

import pandas as pd
import numpy as np
from BERT_converter import BertConverter, BertSentenceConverter
from reduce_function import Reducer
import json
import gzip
import matplotlib.pyplot as plt
from tqdm import tqdm
import matplotlib.patches as mpatches

def read_data(data_dir: str):
    pd_dict = {
        "labels": [],
        "text": [],
        "special_tokens": []
    }
    all_text = ""
    with_floats = ""
    df = pd.read_csv(data_dir, sep=';').T
    headers = df.iloc[0]
    df = pd.DataFrame(df.values[1:], columns=headers)
    df_filtered = df.loc[df['Szenario'].isin(["Web(Patrick)", "VR(Patrick)", "Reference"])]
    print(f"Number of rows: {df_filtered.shape[0]} and number of columns: {df_filtered.shape[1]}")
    for index, row in tqdm(df_filtered.iterrows(), total=df_filtered.shape[0], desc="Reading data"):
        label_i = row["Szenario"]
        text_i = row["Path Description"]
        with_floats += f"{label_i} -> {text_i}\n"
        if not isinstance(text_i, str):
            continue
        all_text += f"{label_i} -> {text_i}\n"
        text_i = text_i.split("->")
        for sentence_i in text_i:
            if sentence_i == "":
                continue
            pd_dict["labels"].append(label_i)
            pd_dict["text"].append(sentence_i)
            pd_dict["special_tokens"].append("")
    
    with open("all_text.txt", "w", encoding="UTF-8") as text_file:
        text_file.write(all_text)
    with open("with_floats.txt", "w", encoding="UTF-8") as txt_file:
        txt_file.write(with_floats)
    return pd_dict


def create_embeddings(data: dict):
    converter = BertSentenceConverter("distiluse-base-multilingual-cased-v2", "cpu")
    embeddings = converter.encode_to_vec(data["text"])
    data["embeddings"] = embeddings
    return data


def reduce_dimensions(data: dict, arts="PACMAP"):
    reducer = Reducer(arts, 2, 42)
    embeddings = reducer.reducer(data["embeddings"], True).tolist()
    for c, vec_i in enumerate(embeddings):
        embeddings[c] = [float(np_float) for np_float in vec_i]
    data["reduced_embeddings"] = embeddings
    return data


def run_pipeline(data_dir: str, output_dir: str, arts="PACMAP"):
    print("Reading data")
    data = read_data(data_dir)
    if os.path.exists(f"{output_dir}/Embeddings.json.gz"):
        with gzip.open(f"{output_dir}/Embeddings.json.gz", "rt", encoding="UTF-8") as json_file:
            data = json.load(json_file)
    else:
        print("Creating embeddings")
        data = create_embeddings(data)
        print("Saving embeddings")
        os.makedirs(os.path.dirname(f"{output_dir}/Embeddings.json.gz"), exist_ok=True)
        with gzip.open(f"{output_dir}/Embeddings.json.gz", "wt", encoding="UTF-8") as json_file:
            json.dump(data, json_file, indent=2)
    if os.path.exists(f"{output_dir}/Data.json.gz"):
        with gzip.open(f"{output_dir}/Data.json.gz", "rt", encoding="UTF-8") as json_file:
            data = json.load(json_file)
    else:
        print("Reducing dimensions")
        data = reduce_dimensions(data, arts)
        print("Saving data")
        out_dir = f"{output_dir}/Data.json.gz"
        os.makedirs(os.path.dirname(out_dir), exist_ok=True)
        with gzip.open(out_dir, "wt", encoding="UTF-8") as json_file:
            json.dump(data, json_file, indent=2)
    fig, ax = plt.subplots(figsize=(10, 10))
    x_points = [i[0] for i in data["reduced_embeddings"]]
    y_points = [i[1] for i in data["reduced_embeddings"]]
    colors = ["red" if i == "Web(Patrick)" else "blue" if i == "VR(Patrick)" else "green" for i in data["labels"]]
    ax.scatter(x_points, y_points, cmap="Spectral", label=data["labels"], c=colors)
    #Legend
    # handles, labels = ax.get_legend_handles_labels()
    # unique_labels = list(set(data["labels"]))
    # unique_labels.sort()
    # ax.legend(handles, unique_labels, title="Szenario")
    ax.legend(title="Szenario")
    ax.grid(True)
    site_patch = mpatches.Patch(color='red', label='SITE')
    nits_patch = mpatches.Patch(color='blue', label='NiTS')
    ref_patch = mpatches.Patch(color='green', label='GPT Prompt')
    plt.legend(handles=[site_patch, nits_patch, ref_patch])

    plt.savefig(f"{output_dir}/text_{arts}.png")


if __name__ == '__main__':
    arts_reducer = ["PCA", "TSNE","PACMAP", "TRIMAP", "UMAP"]
    for art_i in arts_reducer:
        run_pipeline("Data_texts.csv", f"/storage/projects/bagci/data/NewsInTimeAndSpace/{art_i}", art_i)
