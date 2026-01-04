from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util, CrossEncoder
import pandas as pd
import re
import torch

app = FastAPI()

# دالة التنظيف المستخدمة في مشروعك
def clean_arabic_only(text):
    tashkeel = re.compile(r'[\u064B-\u0652\u0640]')
    text = re.sub(tashkeel, '', text)
    text = re.sub(r'[^\u0621-\u064A\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# تحميل النماذج عند بدء التشغيل
print("⏳ جاري تحميل النماذج...")
bi_encoder = SentenceTransformer('sentence-transformers/LaBSE')
cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')

# تحميل وتجهيز البيانات (أول 5000 قصيدة)
file_name = 'Arabic_Poetry_Dataset.csv'
df = pd.read_csv(file_name).head(5000)
all_verses = []
for poem in df['poem_text'].dropna():
    lines = str(poem).split('\n')
    for i in range(0, len(lines), 2):
        if i+1 < len(lines):
            all_verses.append(f"{lines[i]} ... {lines[i+1]}")

print("⏳ جاري إنشاء المتجهات (Embeddings)...")
cleaned_verses = [clean_arabic_only(v) for v in all_verses]
embeddings = bi_encoder.encode(cleaned_verses, convert_to_tensor=True)

@app.get("/search")
def search(query: str):
    query_clean = clean_arabic_only(query)
    query_emb = bi_encoder.encode(query_clean, convert_to_tensor=True)
    
    # البحث الأولي
    hits = util.semantic_search(query_emb, embeddings, top_k=15)[0]
    
    # إعادة الترتيب للتدقيق
    cross_inp = [[query, all_verses[hit['corpus_id']]] for hit in hits]
    cross_scores = cross_encoder.predict(cross_inp)
    
    results = []
    for i in range(len(hits)):
        results.append({
            "verse": all_verses[hits[i]['corpus_id']],
            "score": float(cross_scores[i])
        })
    # ترتيب النتائج حسب الأعلى دقة
    return sorted(results, key=lambda x: x['score'], reverse=True)