"""
Configurações centrais do projeto.
Concentrar pastas, extensões e nomes de modelos aqui evita repetir
esses valores em vários arquivos (e evita divergências como usar
"pdf" em um lugar e "pdfs" em outro).
"""
import os
from pathlib import Path

try:
    # Lê as variáveis do arquivo .env (se existir), como a chave da API.
    # Se o python-dotenv não estiver instalado, o programa continua
    # funcionando com as variáveis de ambiente do sistema.
    from dotenv import load_dotenv

    load_dotenv(Path(__file__).resolve().parent / ".env")

except ImportError:
    pass

# Pastas (sempre relativas à raiz do projeto, e não à pasta onde
# o programa foi executado)
PASTA_BASE = Path(__file__).resolve().parent
PASTA_ARQUIVOS = PASTA_BASE / "arquivos"
PASTA_IMAGENS = PASTA_ARQUIVOS / "imagens"
PASTA_PDFS = PASTA_ARQUIVOS / "pdf"
PASTA_DADOS = PASTA_ARQUIVOS / "dados"

# Arquivo JSON onde os conteúdos e PDFs ficam salvos entre execuções
ARQUIVO_DADOS = PASTA_DADOS / "conteudos.json"

# Extensões de imagem aceitas pelo sistema
EXTENSOES_IMAGEM = (".jpg", ".jpeg", ".png", ".bmp", ".webp")

# Modelo usado para gerar resumos. Pode ser trocado sem mexer no código:
#   Windows (PowerShell):  $env:JOVI_MODELO_RESUMO = "outro/modelo"
MODELO_RESUMO = os.getenv("JOVI_MODELO_RESUMO", "facebook/bart-large-cnn")

# ---------------------------------------------------------------
# OCR
# ---------------------------------------------------------------

# Idioma do OCR: "por" = português (vale para a API e para o Tesseract)
IDIOMA_OCR = "por"

# Qual OCR usar:
#   "ocrspace"  -> API externa OCR.space (padrão). Se a API falhar ou a
#                  chave não estiver configurada, usa o Tesseract local.
#   "tesseract" -> somente o Tesseract instalado no computador (offline).
OCR_PROVEDOR = os.getenv("JOVI_OCR", "ocrspace").strip().lower()

# Chave da API do OCR.space (NUNCA escreva a chave direto no código)
OCR_SPACE_API_KEY = os.getenv("OCR_SPACE_API_KEY", "").strip()
