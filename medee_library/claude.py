from dotenv import load_dotenv
import os
import anthropic
import json

load_dotenv()

key = os.getenv("CLAUDE_KEY")

client = anthropic.Anthropic(
    api_key=key
)

def create_question(content, path):
    content = "Ne réponds qu'en Json. Tu dois te mettre dans la peau d'un médecin en recherche d'informations. Tu te poses des questions que tu cherches sur Google du type : 'test dépistage cancer coloréctal'. La réponse à la question que tu te poses se trouve dans cette ressource (" + path + "):\n" + content + ". Réponds en Json sous ce format avec une liste contenant 3 fois cet objet ({'questions': [{}, {}, {}]}) : {'question_bien_formulee': 'Quel test est utilisé pour le dépistage du cancer colorectal ?', 'question_courte': 'quel test dépistage du cancer colorectal ?', 'question_tres_courte': 'test dépistage cancer colorécral'}"

    message = client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=1000,
        temperature=0,

        messages=[
            {
                "role": "user",
                "content": content
            }
        ]
    )

    try:
        questions = json.loads(message.content[0].text)["questions"]
        q = []
        for chunk in questions:
            for ask in chunk:
                q.append(chunk[ask])

        return q
    except:
        print("Une erreur est survenue lors de la génération de la question par Mistral")
        return []

    # try:
    #     return json.loads(response.choices[0].message.content)["question"]
    # except:
    #     print("Une erreur est survenue lors de la génération de la question par Mistral")
    #     return ""
