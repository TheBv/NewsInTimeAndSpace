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
    dict_data = {}
    x_points = [i[0] for i in data["reduced_embeddings"]]
    y_points = [i[1] for i in data["reduced_embeddings"]]
    colors = ["red" if i == "Web(Patrick)" else "blue" if i == "VR(Patrick)" else "green" for i in data["labels"]]
    shapes = ["o" if i == "Web(Patrick)" else "s" if i == "VR(Patrick)" else "^" for i in data["labels"]]
    counter_text = 0
    for c, label_i in enumerate(data["labels"]):
        if label_i not in dict_data:
            dict_data[label_i] = {
                "x": [],
                "y": [],
                "color": "red" if label_i == "Web(Patrick)" else "blue" if label_i == "VR(Patrick)" else "green",
                "shape": "o" if label_i == "Web(Patrick)" else "s" if label_i == "VR(Patrick)" else "^",
                "counter": [],
                "text": []
            }
        dict_data[label_i]["x"].append(x_points[c])
        dict_data[label_i]["y"].append(y_points[c])
        dict_data[label_i]["counter"].append(counter_text)
        dict_data[label_i]["text"].append(data["text"][counter_text])
        counter_text += 1
    for label_i in dict_data:
        # draw every point with different color and shape and write the number of the point
        ax.scatter(dict_data[label_i]["x"], dict_data[label_i]["y"], cmap="Spectral", label=label_i, c=dict_data[label_i]["color"], marker=dict_data[label_i]["shape"], s=50)
        for c, txt in enumerate(dict_data[label_i]["text"]):
            ax.text(dict_data[label_i]["x"][c], dict_data[label_i]["y"][c], dict_data[label_i]["counter"][c])
    # ax.scatter(x_points, y_points, cmap="Spectral", label=data["labels"], c=colors, markers=shapes)
    #Legend
    # handles, labels = ax.get_legend_handles_labels()
    # unique_labels = list(set(data["labels"]))
    # unique_labels.sort()
    # ax.legend(handles, unique_labels, title="Szenario")
    # ax.legend(title="Szenario")
    # ax.grid(True)
    # site_patch = mpatches.Patch(color='red', label='SITE')
    # nits_patch = mpatches.Patch(color='blue', label='NiTS')
    # ref_patch = mpatches.Patch(color='green', label='GPT Prompt')
    # plt.legend(handles=[site_patch, nits_patch, ref_patch])
    # legend with color and markers
    ax.legend(title="Szenario", loc="upper right")
    # write an extra Legend outside the plot the text to the number of the point with shape and color
    counter_text = 0
    for label_i in dict_data:
        for c, txt in enumerate(dict_data[label_i]["text"]):
            ax.text(1.1, 0.9 - counter_text * 0.1, f"{dict_data[label_i]['counter'][c]} -> {txt}", transform=ax.transAxes)
            counter_text += 0.2
    plt.tight_layout()
    plt.savefig(f"/storage/projects/bagci/data/NewsInTimeAndSpace/text_{arts}.png", bbox_inches = "tight")


if __name__ == '__main__':
    arts_reducer = ["PCA", "TSNE", "PACMAP", "TRIMAP", "UMAP"]
    for art_i in arts_reducer:
        run_pipeline("Data_texts.csv", f"/storage/projects/bagci/data/NewsInTimeAndSpace/{art_i}", art_i)
