from dotenv import load_dotenv
import os
import json
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

load_dotenv()

key = os.getenv("MISTRAL_KEY")

client = MistralClient(api_key=key)

def create_embeddings(datas):
    embeddings_batch_response = client.embeddings(
        model="mistral-embed",
        input=datas,
    )

    return embeddings_batch_response.data[0].embedding

def create_question(content, path):
    messages = [
        ChatMessage(role="user", content=f"Tu joues le role d'un médecin qui se pose des questions. Basé sur une ressource de '{path}', voici le contenu de la ressource : \n{content}\nTu dois créer une très courte question qu'un médecin généraliste pourrait se poser et donc la réponse est dans la ressource. Réponds moi en Json ('question': 'xxx') ")
    ]

    response = client.chat(
        model="mistral-large-latest",
        response_format={"type": "json_object"},
        messages=messages,
        temperature=0.1
    )

    try:
        return json.loads(response.choices[0].message.content)["question"]
    except:
        print("Une erreur est survenue lors de la génération de la question par Mistral")
        return ""
