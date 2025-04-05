# vector_representations.py
from transformers import BertModel
import torch

model = BertModel.from_pretrained('bert-base-multilingual-cased', output_hidden_states=True)

def get_bert_embeddings(text, tokenizer):
    inputs = tokenizer(
        text,
        padding='max_length',
        truncation=True,
        max_length=512,
        return_tensors='pt'
    )
    with torch.no_grad():
        outputs = model(**inputs)
    # Используем предпоследний слой (12-й слой из 13)
    hidden_states = outputs.hidden_states[-2]
    # Усреднение по токенам
    return torch.mean(hidden_states, dim=1).squeeze().numpy().tolist()