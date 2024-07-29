from transformers import AutoModel, AutoTokenizer
import torch

# model_name = "Dr-BERT/DrBERT-7GB-Large"
model_name = "Alibaba-NLP/gte-Qwen2-1.5B-instruct"
# model_name = "dunzhang/stella_en_1.5B_v5"

tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModel.from_pretrained(model_name)

def create_embeddings(d):
    """
    Création d'embeddings à partir d'un modèle hugging face

    INPUT :
        d = données a transformer en embedddings

    RETURN : embeddings en format liste python et non Tensor([])
    """
    inputs = tokenizer(d, return_tensors="pt", padding=True, truncation=True)

    with torch.no_grad():
        outputs = model(**inputs)
        embedding = outputs.last_hidden_state.mean(dim=1)

        return embedding.tolist()[0]
