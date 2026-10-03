from sentence_transformers import SentenceTransformer
import faiss
import numpy as np


model = SentenceTransformer('all-MiniLM-L6-v2')

s = ["red", "hello", "sky", "color", "pen", "Blue", "create"]
q = "face"

s_vectors = np.array(model.encode(s))
q_vectors = np.array(model.encode([q]))



d = 384 # Dimensionality of embeddings (e.g., from BERT)
index = faiss.IndexFlatL2(d)

print(index)
print(type(index))
exit()
index.add(s_vectors) # Example data

print(f"indexed {index.ntotal}")

k = len(s)
distances, indices = index.search(q_vectors, k)

for i in indices[0]:
    print(f"found: {s[i]}")