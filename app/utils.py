import numpy as np
from scipy.spatial.distance import cosine

def cosine_similarity(a, b):
    a=np.array(a)
    b=np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def get_cosine_similarity(v1, v2):
    # Chuyển về numpy array nếu chưa phải
    v1 = np.array(v1)
    v2 = np.array(v2)
    
    # Tính tích vô hướng (dot product)
    dot_product = np.dot(v1, v2)
    
    # Tính độ dài (norm) của từng vector
    norm_v1 = np.linalg.norm(v1)
    norm_v2 = np.linalg.norm(v2)
    
    # Tránh lỗi chia cho 0 nếu vector rỗng
    if norm_v1 == 0 or norm_v2 == 0:
        return 0.0
        
    return dot_product / (norm_v1 * norm_v2)