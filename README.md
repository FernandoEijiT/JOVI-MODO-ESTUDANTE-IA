# Modo Estudante - JOVI

Aplicação de terminal em Python que ajuda estudantes a organizar conteúdos de estudo.
Ela captura textos ou imagens, extrai o texto das imagens com OCR, gera resumos
automáticos e exporta tudo em PDF.

## Funcionalidades

- Capturar conteúdo digitado ou o caminho de uma imagem
- Melhorar a imagem com OpenCV (ruído, nitidez, contraste)
- Extrair o texto da imagem com OCR: **API externa OCR.space** ou **Tesseract local**
- Gerar resumo automático do conteúdo (modelo BART via Transformers)
- Detectar se o texto parece um documento (título, capítulo, introdução, conclusão...)
- Listar, buscar (sem diferenciar maiúsculas/acentos), editar e remover conteúdos
- Gerar PDF com título, resumo e conteúdo original
- **Persistência em JSON**: conteúdos e PDFs gerados ficam salvos em `arquivos/dados/conteudos.json` e são recarregados na próxima execução
- Logo após capturar um texto ou processar uma imagem, o programa pergunta se deseja ativar o **Modo Estudante** (insiste até receber sim/não válido); se o conteúdo parecer um documento (título, capítulo, introdução, resumo, conclusão, referência), um aviso é exibido antes da pergunta

## API externa utilizada

**OCR.space** (https://ocr.space/ocrapi): a imagem é enviada por HTTP (POST) para
`https://api.ocr.space/parse/image` e a API devolve o texto reconhecido em JSON.
O plano gratuito permite 25.000 requisições por mês, até 500 por dia, com arquivos de
até 1 MB (o programa reduz a imagem automaticamente antes de enviar).

Se a API falhar (sem internet, sem chave, limite excedido), o programa usa o
Tesseract local como alternativa.

## Estrutura do projeto

```
JOVI-MODO-ESTUDANTE-IA/
├── app.py                  # ponto de entrada
├── configuracao.py         # pastas, extensões, modelo de resumo e configurações do OCR
├── requirements.txt        # dependências Python
├── .env.example            # modelo do arquivo .env (chave da API)
├── modelos/                # classes que representam os dados
│   ├── conteudo.py         # Conteudo (texto, resumo, imagem, modo estudante)
│   └── pdf.py              # PDF (nome e origem do arquivo gerado)
├── servicos/               # regras e integrações com bibliotecas
│   ├── armazenamento.py    # persistência em JSON (salvar/carregar)
│   ├── captura.py          # validação da entrada e normalização de texto
│   ├── documento.py        # detecção de documentos por palavras-chave
│   ├── imagem.py           # leitura, gravação e melhoria de imagens (OpenCV)
│   ├── ocr.py              # OCR local (Tesseract)
│   ├── ocr_space.py        # OCR por API externa (OCR.space)
│   ├── resumo.py           # geração de resumos (Transformers)
│   └── pdf.py              # geração de PDFs (ReportLab)
├── sistema/
│   └── modo_estudante.py   # menu e fluxo principal da aplicação
└── arquivos/
    ├── dados/              # conteudos.json (gerado pelo programa)
    ├── imagens/            # imagens melhoradas
    └── pdf/                # PDFs gerados
```

## Instalação

1. **Python 3.10 ou superior**
2. Instale as bibliotecas:

```bash
pip install -r requirements.txt
```

3. Configure a chave da API:
   - Crie uma chave gratuita em https://ocr.space/ocrapi
   - Copie o arquivo `.env.example` para `.env`
   - Abra o `.env` e troque `cole_sua_chave_aqui` pela sua chave

   O arquivo `.env` está no `.gitignore`, então a chave não vai para o GitHub.

4. **(Opcional, mas recomendado) Tesseract OCR**, usado como alternativa quando a API
   não está disponível, ou como OCR principal no modo offline:
   - Windows: instalador em https://github.com/UB-Mannheim/tesseract/wiki
     (marque "Portuguese" durante a instalação)
   - Linux (Debian/Ubuntu): `sudo apt install tesseract-ocr tesseract-ocr-por`

   O programa procura o Tesseract automaticamente (variável `TESSERACT_CMD`, PATH ou
   pasta padrão do Windows). Para conferir o idioma: `tesseract --list-langs`
   (a lista precisa conter `por`).

## Como executar

```bash
python app.py
```

### Escolhendo o OCR

No arquivo `.env`, a variável `JOVI_OCR` define qual OCR usar:

| Valor        | Comportamento                                                        |
|--------------|----------------------------------------------------------------------|
| `ocrspace`   | API OCR.space (padrão); se falhar, usa o Tesseract local             |
| `tesseract`  | Somente o Tesseract local, sem internet e sem chave de API           |

Na primeira vez que um resumo for gerado, o modelo é baixado da internet
(algumas centenas de MB) e isso pode demorar. Depois fica salvo no computador.

## Persistência de dados

A cada captura, edição, remoção ou geração de PDF o programa grava o estado em
`arquivos/dados/conteudos.json` (UTF-8). Ao iniciar, ele lê esse arquivo e continua de onde parou.
Se o arquivo estiver corrompido, ele é renomeado para `conteudos.json.corrompido` e o programa
inicia vazio, sem travar.

## Configurações opcionais

- `JOVI_MODELO_RESUMO`: troca o modelo de resumo (padrão: `facebook/bart-large-cnn`).
  O modelo padrão foi treinado em inglês, então os resumos de textos em português
  podem ter qualidade limitada.
- `TESSERACT_CMD`: caminho completo do executável do Tesseract, se ele estiver
  instalado em outro local.

## Tecnologias

Python, OpenCV, OCR.space API, Tesseract (pytesseract), Transformers (PyTorch),
requests, python-dotenv e ReportLab.
