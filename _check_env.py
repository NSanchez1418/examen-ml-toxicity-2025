import sys, subprocess

print("python", sys.version)

# --- NLTK stopwords ---
import nltk
try:
    nltk.data.find('corpora/stopwords')
    print('nltk stopwords: OK')
except LookupError:
    nltk.download('stopwords')
    print('nltk stopwords: descargadas')

# --- spaCy es_core_news_sm ---
import spacy
try:
    spacy.load('es_core_news_sm')
    print('spacy es_core_news_sm: OK')
except OSError:
    subprocess.run([sys.executable, '-m', 'spacy', 'download', 'es_core_news_sm'], check=True)
    spacy.load('es_core_news_sm')
    print('spacy es_core_news_sm: instalado')
