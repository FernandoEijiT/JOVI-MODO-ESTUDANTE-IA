import os
from pathlib import Path

try:
    # Lê o arquivo .env (chave da API, etc.). Sem o python-dotenv, usa só as
    # variáveis de ambiente do sistema.
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")

except ImportError:
    pass

# Pastas
PASTA_BASE = Path(__file__).resolve().parent
PASTA_ARQUIVOS = PASTA_BASE / "arquivos"
PASTA_IMAGENS = PASTA_ARQUIVOS / "imagens"
PASTA_PDFS = PASTA_ARQUIVOS / "pdf"
PASTA_DADOS = PASTA_ARQUIVOS / "dados"

# Onde os conteúdos e PDFs ficam salvos entre execuções
ARQUIVO_DADOS = PASTA_DADOS / "conteudos.json"

EXTENSOES_IMAGEM = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# ---------------------------------------------------------------
# Resumo
# ---------------------------------------------------------------

# "transformers" -> modelo de IA (precisa baixar o modelo na primeira vez)
# "simples"      -> resumo por frases, leve e sem baixar nada
# Se o modelo não carregar, o programa usa o simples automaticamente.
RESUMO_PROVEDOR = os.getenv("JOVI_RESUMO", "transformers").strip().lower()

# Modelo treinado para resumir textos em português
MODELO_RESUMO = os.getenv("JOVI_MODELO_RESUMO", "recogna-nlp/ptt5-base-summ")

# O PTT5 usa o tokenizador de outro repositório; nos demais modelos é o próprio
TOKENIZADOR_RESUMO = os.getenv(
    "JOVI_TOKENIZADOR_RESUMO",
    "unicamp-dl/ptt5-base-portuguese-vocab"
    if MODELO_RESUMO == "recogna-nlp/ptt5-base-summ"
    else MODELO_RESUMO,
)

# ---------------------------------------------------------------
# OCR
# ---------------------------------------------------------------

# "por" = português (vale para a API e para o Tesseract)
IDIOMA_OCR = "por"

# "ocrspace"  -> API externa OCR.space (padrão), com Tesseract como alternativa
# "tesseract" -> somente o Tesseract local (offline)
OCR_PROVEDOR = os.getenv("JOVI_OCR", "ocrspace").strip().lower()

# Chave da API (fica no .env, nunca no código)
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "").strip()
