from medee_library.files import clean_and_parse_markdown, list_files_in_dir, clean_text, split_markdown
from medee_library.model import create_embeddings
from medee_library.qdrant import add_vector
from medee_library.mistral import create_question, create_embeddings as create_embeddings_mistral
from medee_library.claude import create_question as create_question_claude

markdowns = list_files_in_dir("./recommandations")

print(len(markdowns), "files found !")

embeddings_counter = 0

def create_obj(path, metadata, content, isSchema):
    """
    On créé l'objet de metadata pour le stocker avec le vecteur dans qdrant

    INPUT :
        path = chemin du contenu (ex: titre du document + sous-titre + sous-sous titre)
        metadata = objet de metadonnées extrait au début de chaque markdown
        content = contenu nettoyé
        isSchema = est ce que le contenu est un schema ?

    RETURN : {
            path,
            title,
            lastmod,
            specialites,
            sources,
            isSchema,
            content
        }
    """
    return {
        "path": path,
        "title": metadata["title"],
        "lastmod": metadata["lastmod"],
        "specialities": metadata["specialites"],
        "sources": metadata["sources"],
        "isSchema": isSchema,
        "content": content
    }

def create_embeddings_and_uplpoad_qdrant(collection_name, path, metadata, content, isSchema, id):
    """
    Fonction wrapper pour créer les embeddings, les payloads et ajouter les vecteurs a qdrant

    INPUT :
        collection_name = nom de la collection qdrant à laquelle ajouter les vecteurs
        path = chemin du contenu (ex: titre du document + sous-titre + sous-sous titre)
        metadata = objet de metadonnées extrait au début de chaque markdown
        content = contenu nettoyé
        isSchema = est ce que le contenu est un schema ?
        id = id du vecteur

    RETURN : void
    """
    # embeddings = create_embeddings(path) # on demande l'embedding depuis le path du document (on embed pas le contenu mais le path)
    embeddings = create_embeddings_mistral(path)
    payload = create_obj(path, metadata, content, isSchema) # on créé l'objet de metadata du vecteur pour qdrant
    status = add_vector(collection_name, embeddings, payload, id) # on ajoute le vecteur a qdrant

    if status:
        print("Vector", id, "added")
    else:
        print("Err vector", id)

def get_data(collection_name):
    """
    On map tous les fichiers markdown pour en extraire leur contenu nettoyé, séparé en sous titre et sous-sous titre

    INPUT :
        collection_name = nom de la collection qdrant à laquelle ajouter les vecteur

    RETURN : void
    """
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
                        create_embeddings_and_uplpoad_qdrant(collection_name, path, metadata, previous_chunk, False, i)
                        i += 1
                else: # nous avons un graph
                    title = section_content.split('title="')[1].split(".")[0].lower() # ici c'est le titre du graphique qui est extrait
                    create_embeddings_and_uplpoad_qdrant(collection_name, title, metadata, previous_chunk, True, i)
                    i += 1

            for under_section_title, under_section_content in split_markdown(clean): # pour chaque sous-sous titre, on map
                path = title + " " + section_title + " " + under_section_title
                path = path.lower()
                create_embeddings_and_uplpoad_qdrant(collection_name, path, metadata, under_section_content, False, i)

                i += 1

def get_data_to_create_question(claude = False):
    """
    On map tous les fichiers markdown pour en extraire leur contenu nettoyé, séparé en sous titre et sous-sous titre

    RETURN : an object containing all generated questions in this format : {"0": "question0", "1": "question1", ...}
    """
    i = 0

    obj = {}

    for mark in markdowns:
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
                        if claude:
                            q = create_question_claude(previous_chunk, path)
                            obj[str(i)] = q
                            if q != []:
                                print(i, "ok")
                        else:
                            q = create_question(previous_chunk, path)
                            obj[str(i)] = q
                            if q != "":
                                print(i, "ok")

                        i += 1
                else: # nous avons un graph
                    title = section_content.split('title="')[1].split(".")[0].lower() # ici c'est le titre du graphique qui est extrait
                    if claude:
                        q = create_question_claude(previous_chunk, path)
                        obj[str(i)] = q
                        if q != []:
                            print(i, "ok")
                    else:
                        q = create_question(previous_chunk, path)
                        obj[str(i)] = q
                        if q != "":
                            print(i, "ok")

                    i += 1

            for under_section_title, under_section_content in split_markdown(clean): # pour chaque sous-sous titre, on map
                path = title + " " + section_title + " " + under_section_title
                path = path.lower()
                if claude:
                    q = create_question_claude(under_section_content, path)
                    obj[str(i)] = q
                    if q != []:
                        print(i, "ok")
                else:
                    q = create_question(under_section_content, path)
                    obj[str(i)] = q
                    if q != "":
                        print(i, "ok")

                i += 1

    return obj
