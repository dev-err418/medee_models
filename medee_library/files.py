import os
import re

def list_files_in_dir(dir):
    """
    Lister tous les fichiers markdown dans un dossier

    INPUT :
        dir = le dossier dans lequel chercher les markdowns

    RETURN : une liste de tous les noms de fichiers markdowns contenus dans le dossier
    """
    return [f for f in os.listdir(dir) if os.path.isfile(os.path.join(dir, f)) and f.endswith(".md")]

def read_file(path):
    """
    Lire le contenu d'un fichier

    INPUT :
        path = chemin du fichier à lire

    RETURN : le contenu du fichier
    """
    with open(path, "r", encoding="utf-8") as file:
        content = file.read()

    return content

def extract_article_summary(content):
    """
    Extraire le résumé d'un article de reco médicales

    INPUT :
        content = le contenu d'un article markdown de reco médicales

    RETURN : si l'article contient un résumé, on le renvoit brut sinon on renvoit None
    """
    pattern = r'{{\%article-summary\%}}(.*?){{\%\/article-summary\%}}'
    match = re.search(pattern, content, re.DOTALL)

    if match:
        return match.group(1).strip()
    else:
        return None

def find_all_collapsible_sections(content):
    """
    Trouver tous les passages retractables

    INPUT :
        content = le contenu d'un article markdown de reco médicales

    RETURN : toutes les itterations de passages retractables
    """
    pattern = r'{{\%collapse\s+"(.*?)"\s+%}}(.*?){{\%\s*/collapse\s+%}}'
    matches = re.findall(pattern, content, re.DOTALL)

    return matches

def extract_all_sources(content):
    """
    Extraire toutes les sources d'un article de reco médicales

    INPUT :
        content = le contenu d'un article markdown de reco médicales

    RETURN : une liste des sources en tuple (nom source, url)
    """
    pattern = r'{{\%sources\%}}([\s\S]*?){{\%\/sources\%}}'
    matches = re.findall(pattern, content)

    sources = []
    for match in matches:
        lines = match.strip().split('\n')

        for line in lines:
            if line.startswith('- ['):
                title_pattern = r'-\s*\[(.*?)\]\s*\((.*?)\)'
                title_match = re.match(title_pattern, line)
                if title_match:
                    title = title_match.group(1)
                    url = title_match.group(2)
                    sources.append((title, url))
            elif line.startswith('### Bibliographie en attente'):
                break

    return sources

def clean_text(content):
    """
    Nettoye le texte de tout le formattage de reco médicales

    INPUT :
        content = le contenu d'un article de reco médicales

    RETURN : le texte nettoyé
    """
    pattern1 = r'\{\{<\s*modal-btn[^>]+>\}\}(.*?)\{\{<\s*/modal-btn\s*>\}\}'
    pattern2 = r'\{\..*?\}'
    pattern3 = r'\*?\[(.*?)\]\(.*?\)\*?'
    pattern4 = r'\{\{<\s*card-link(?:-external)?\s+.*?\}\}'
    pattern5 = r'\n: '
    pattern6 = r'\{\{%\s*\w+\s*%\}\}.*?\{\{%\s*/\w+\s*%\}\}'

    cleaned_text = re.sub(pattern1, r'\1', content)
    cleaned_text = re.sub(pattern2, '', cleaned_text)
    cleaned_text = re.sub(pattern3, r'\1', cleaned_text)
    cleaned_text = re.sub(pattern4, '', cleaned_text, flags=re.DOTALL)
    cleaned_text = re.sub(pattern5, ': ', cleaned_text)
    cleaned_text = re.sub(pattern6, '', cleaned_text, flags=re.DOTALL)

    return cleaned_text

def split_markdown(markdown_text):
    """
    Séctionne le contenu d'une recommendation reco médicales en fonction des titres markdown

    INPUT :
        markdown_text = contenu nettoyé d'une recommendation

    RETURN : une liste de tuples (titre, contenu)
    """
    sections = markdown_text.split("### ")
    markdown_list = []

    for i in range(1, len(sections)):
        key = sections[i].split("\n")[0]
        value = "\n".join(sections[i].split("\n")[1:])
        markdown_list.append((key, value))

    return markdown_list


def clean_and_parse_markdown(file_path):
    """
    Wrapper qui permet d'extraires les metadatas, nettoyer le markdown et le parser

    INPUT :
        file_path = chemin d'accès au fichier à extraire

    RETURN :
        les metadatas,
        le résumé,
        les sources,
        les sections en liste de tuples (titre, contenu)
    """
    content = read_file(file_path)

    parts = content.split('+++', 2)
    if len(parts) == 3:
        frontmatter_raw, main_content = parts[1], parts[2]
    else:
        frontmatter_raw, main_content = '', content

    metadata = {}
    for line in frontmatter_raw.strip().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"')
            metadata[key] = value

    summary = extract_article_summary(main_content)
    sources = extract_all_sources(main_content)
    sections = find_all_collapsible_sections(main_content)

    return metadata, summary, sources, sections

def get_title_wrapper(file_path):
    """
    Wrapper qui permet d'extraires les metadatas

    INPUT :
        file_path = chemin d'accès au fichier à extraire

    RETURN :
        les metadatas
    """
    content = read_file(file_path)

    parts = content.split('+++', 2)
    if len(parts) == 3:
        frontmatter_raw, main_content = parts[1], parts[2]
    else:
        frontmatter_raw, main_content = '', content

    metadata = {}
    for line in frontmatter_raw.strip().split('\n'):
        if '=' in line:
            key, value = line.split('=', 1)
            key = key.strip()
            value = value.strip().strip('"')
            metadata[key] = value

    return metadata
