from mistralai.client import MistralClient

key = ""

client = MistralClient(api_key=key)

def create_embeddings(datas):
    embeddings_batch_response = client.embeddings(
        model="mistral-embed",
        input=datas,
    )

    return embeddings_batch_response.data[0].embedding
