"""
Permet de benchmarker le dense model en 2 types de tests
"""
import json
from medee_library.model import create_embeddings
# from medee_library.mistral import create_embeddings
from medee_library.qdrant import run_query, run_filter
from medee_library.files import list_files_in_dir, get_title_wrapper
import numpy as np
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score
from sklearn.preprocessing import LabelEncoder

collection_name = "reco_alibaba"

with open("dense.json", "r") as f:
    data = json.load(f)

top_1 = []
top_3 = []
top_5 = []

def check_top_1_or_3_or_5(results, vec_id):
    """
    Determine le top

    INPUT :
        results = liste des résultats qdrant
        vec_id = id du vecteur cible (vecteur pour lequel la question a été générée)

    RETURN : void
    """
    for i, point in enumerate(results):
        if point.id == vec_id:
            if i == 0:
                return top_1.append(vec_id)
            elif i <= 2:
                return top_3.append(vec_id)
            else:
                return top_5.append(vec_id)

    return -1

def get_accuracy_wrapper(min_no_q, vec_id):
    """
    Wrapper pour connaitres la précision top 1, 3 et 5

    INPUT:
        min_no_q = question en minuscule sans "?"
        vec_id = id du vecteur cible (vecteur pour lequel la question a été générée)


    RETURN : void
    """
    emb_min_no_q = create_embeddings(min_no_q)

    check_top_1_or_3_or_5(run_query(collection_name, emb_min_no_q, 5), vec_id)

def get_top_accuracy():
    """
    Permet de connaitre la precision top 1, 3 et 5

    RETURN : void
    """
    i = 0
    for index in data:
        el = data[index]

        el_maj_q = el # avec "?" et avec majuscules
        el_min_q = el.lower() # avec "?" + sans majuscules
        el_maj_no_q = el.replace("?", "") # sans "?" avec majuscules
        el_min_no_q = el_maj_no_q.lower() # sans "?" + sans majuscules

        get_accuracy_wrapper(el_min_no_q, i)

        print(i, "ok")
        i += 1

get_top_accuracy()

print("Top 1", len(top_1)/len(data))
print("Top 3", len(top_1 + top_3)/len(data))
print("Top 5", len(top_1 + top_3 + top_5)/len(data))

def get_clusterisation():
    """
    Permet d'évaluer la clusterisation d'une collection qdrant
    RETURN : void
    """
    file_names = list_files_in_dir("./recommandations")
    obj = {}
    for file_name in file_names:
        title = get_title_wrapper("./recommandations/" + file_name)["title"]
        print(title)
        points = run_filter(collection_name, title)
        p = []
        for point in points:
            # Ensure the vector is a list of floats
            if isinstance(point.vector, (list, np.ndarray)):
                p.append(point.vector)
            else:
                print(f"Unexpected vector format for title {title}: {type(point.vector)}")
        if p:  # Only add if we have valid vectors
            obj[title] = p

    embeddings = []
    categories = []
    for category, embed_list in obj.items():
        embeddings.extend(embed_list)
        categories.extend([category] * len(embed_list))

    if not embeddings:
        print("No valid embeddings found.")
        return

    embeddings = np.array(embeddings)

    # Check the shape of embeddings
    if len(embeddings.shape) == 1:
        print(f"Embeddings shape is 1D: {embeddings.shape}. Attempting to reshape...")
        # Reshape to 2D if it's a single feature
        embeddings = embeddings.reshape(-1, 1)
    elif len(embeddings.shape) > 2:
        print(f"Unexpected embedding shape: {embeddings.shape}. Flattening to 2D...")
        embeddings = embeddings.reshape(embeddings.shape[0], -1)

    print(f"Final embeddings shape: {embeddings.shape}")

    le = LabelEncoder()
    category_encoded = le.fit_transform(categories)

    try:
        silhouette = silhouette_score(embeddings, category_encoded)
        calinski_harabasz = calinski_harabasz_score(embeddings, category_encoded)
        davies_bouldin = davies_bouldin_score(embeddings, category_encoded)

        print(f"Silhouette Score: {silhouette}")
        print(f"Calinski-Harabasz Index: {calinski_harabasz}")
        print(f"Davies-Bouldin Index: {davies_bouldin}")
    except ValueError as e:
        print(f"Error calculating scores: {e}")
        print(f"Embeddings shape: {embeddings.shape}")
        print(f"Categories shape: {category_encoded.shape}")
        print(f"Sample embedding: {embeddings[0]}")
        print(f"Sample category: {category_encoded[0]}")

# get_clusterisation()
