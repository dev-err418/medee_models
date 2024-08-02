"""
Choisir une fonction entre la création du dataset 'sparse.json' avec Claude ou bien la génération du dataset en triplets
"""

# from medee_library.scrape import get_data_to_create_question
from medee_library.files import list_files_in_dir, clean_and_parse_markdown, clean_text, split_markdown
import json
import ast
import random

collection_name = "reco_alibaba"

def create_dataset_w_claude():
    """
    Fonction utilisée pour créer le dataset avec Claude. Pour chaque vecteur, on créé 9 questions :
        3 * ["question bien formulée", "question mots-clés formulée", "question mots-clés"]

    RETURN : void
    """
    pass
    # data = get_data_to_create_question(claude=True)

    # with open("sparse.json", "w") as f:
    #   json.dump(data, f, indent=4)

with open("sparse.json", "r") as f:
    data = json.load(f)

def get_data():
    """
    On map tous les fichiers markdown pour en extraire leur contenu nettoyé, séparé en sous titre et sous-sous titre

    RETURN :
        chunks (an object of each chunk and its title and content)
    """
    markdowns = list_files_in_dir("./recommandations")

    chunks = {}
    i = 0
    for mark in markdowns:
        # if i >= 10:
        #     break
        metadata, summary, sources, sections = clean_and_parse_markdown("./recommandations/" + mark)

        title = metadata["title"]
        lastmod = metadata["lastmod"]
        specialites = metadata["specialites"] # array
        sources = metadata["sources"] # array of source names

        for section_title, section_content in sections:
            clean = clean_text(section_content) # on nettoye le texte de tous les formattages qui pourraient géner les embeddings

            if clean.split("###")[0]: # on vérifie s'il n'existe pas du texte avant le premier sous titre
                path = title + " " + section_title
                path = path.lower()
                previous_chunk = clean.split("###")[0]
                if "mermaid" not in section_content: # on vérifie si ce texte avant le premier sous titre n'est pas un schema
                    if previous_chunk.strip(): # est ce que le texte avant n'est pas vide ? (que des \n ou des espaces)
                        chunks[str(i)] = {
                            "specialities": metadata["specialites"],
                            "content": previous_chunk
                        }
                        i += 1
                else: # nous avons un graph
                    title = section_content.split('title="')[1].split(".")[0].lower() # ici c'est le titre du graphique qui est extrait
                    chunks[str(i)] = {
                        "specialities": metadata["specialites"],
                        "content": previous_chunk
                    }
                    i += 1

            for under_section_title, under_section_content in split_markdown(clean): # pour chaque sous-sous titre, on map
                path = title + " " + section_title + " " + under_section_title
                path = path.lower()
                chunks[str(i)] = {
                    "specialities": metadata["specialites"],
                    "content": under_section_content
                }

                i += 1
    return chunks

def generate_triplet_dataset():
    def filter_contents(data, exclude_specialities):
        """
        Prends en entrée les datas et les spécialités à enlever, pour renvoyer une liste de content qui ne contiennent pas ces spés

        INPUT :
            data = les données d'entrée à trier
            explude_specialities = liste de spécialités à enlever

        OUTPUT :
            une liste de content
        """
        return [
            item["content"]
            for item in data.values()
            if not any(spe in item["specialities"] for spe in exclude_specialities)
        ]

    with open("sparse.json", "r") as f:
        data = json.load(f)

    chunks = get_data()

    ds = []

    for chunk_id in data:
        chunk = chunks[chunk_id]

        spes = chunk["specialities"]
        spes_list = ast.literal_eval(spes)

        contents = filter_contents(chunks, spes_list)
        if (len(contents) == 0):
            print("Aucun contenu pour les spécialités suivantes", spes_list)
            print("Chunk id:", chunk_id)

        for question in data[chunk_id]:
            random_content_index = random.randint(0, len(contents) - 1)
            random_content = contents[random_content_index]

            question_cleaned = question.replace(" ?", "").lower()

            ds.append({
                "anchor": question_cleaned,
                "positive": chunk["content"],
                "negative": random_content
            })

    with open("sparse_triplet.json", "w") as f:
        json.dump(ds, f, indent=4)


generate_triplet_dataset()
