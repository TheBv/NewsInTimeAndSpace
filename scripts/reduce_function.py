from typing import Any
import numpy as np
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn.preprocessing import StandardScaler
#from pacmap import PaCMAP
#from trimap import TRIMAP
#from umap import UMAP


class Reducer:
    def __init__(self, r_function_name: str, n_compt: int, random_state: Any = None):
        self.r_function_name = r_function_name
        self.n_compt = n_compt
        self.random_state = random_state

    def reducer(self, vector_matrix: list, scaling: bool = False):
        matrix_embeddings = vector_matrix
        # list to np_array
        matrix_embeddings = np.array(matrix_embeddings)
        # Fit_function Variants
        algo = None
        if self.r_function_name == "PCA":
            algo = PCA(n_components=self.n_compt, random_state=self.random_state)
        elif self.r_function_name == "TSNE":
            algo = TSNE(n_components=self.n_compt, n_jobs=6, random_state=self.random_state)
        elif self.r_function_name == "PACMAP":
            algo = PaCMAP(n_components=self.n_compt, n_neighbors=None, random_state=self.random_state)
        elif self.r_function_name == "TRIMAP":
            algo = TRIMAP(n_dims=self.n_compt)
        elif self.r_function_name == "UMAP":
            algo = UMAP(n_components=self.n_compt, random_state=self.random_state)
        if algo:
            x_embeddings = algo.fit_transform(matrix_embeddings)
        else:
            x_embeddings = matrix_embeddings
        # Standard_scaler (I would recommend it) https://scikit-learn.org/stable/modules/manifold.html#tips-on-practical-use
        if scaling:
            x_embeddings = StandardScaler().fit_transform(x_embeddings)
        return x_embeddings