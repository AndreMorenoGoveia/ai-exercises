# Classificação de emoções com Transformers congelados

- `classificacao_emocoes.ipynb`: notebook executado (embeddings, validação cruzada, métricas, matrizes de confusão).
- `relatorio/relatorio.pdf`: relatório (fonte em `relatorio/relatorio.tex`).
- `data/`: CSVs do Emotion Dataset (Kaggle, parulpandey/emotion-dataset).
- `embeddings/`: vetores 20.000 × 768 de cada encoder (176 MB, fora do ZIP). São regenerados pelo notebook em poucos minutos com GPU, ou podem ser fornecidos por link externo.
- `models/`: Pipelines treinados de cada fold (joblib).
- `results/`: folds, predições out-of-fold, métricas em CSV e figuras.

Requisitos: Python 3.12, torch, transformers, scikit-learn, pandas, matplotlib, joblib, sentencepiece.
Rodar com o notebook na pasta `project/`. Arquivos já presentes em disco são carregados em vez de recalculados.
