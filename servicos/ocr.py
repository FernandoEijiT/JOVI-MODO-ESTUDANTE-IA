import os
import shutil
import pytesseract
from configuracao import IDIOMA_OCR
from servicos.imagem import ServicoImagem

class ServicoOCR:
    """OCR local: lê o texto de imagens com o Tesseract instalado no computador."""

    # Locais onde o instalador do Tesseract costuma colocar o executável
    CAMINHOS_WINDOWS = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    )

    def __init__(self, idioma=IDIOMA_OCR):
        """Cria o serviço com o idioma do OCR (por padrão, o IDIOMA_OCR) e já tenta
        achar o Tesseract sozinho.
        """
        self._idioma = idioma
        self._configurado = False

        self._configurar_automaticamente()

    @property
    def configurado(self):
        """Devolve True se o Tesseract foi encontrado e está configurado."""
        return self._configurado

    def configurar(self, caminho_tesseract):
        """Define o caminho do executável do Tesseract. Levanta FileNotFoundError
        se o caminho não existir.
        """
        if not os.path.exists(caminho_tesseract):
            raise FileNotFoundError(
                "O caminho do Tesseract não foi encontrado."
            )

        pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

        self._configurado = True

    def _configurar_automaticamente(self):

        """Procura o Tesseract na variável TESSERACT_CMD, no PATH e nas pastas onde
        o instalador do Windows costuma colocá-lo.
        """
        candidatos = [
            os.getenv("TESSERACT_CMD"),
            shutil.which("tesseract"),
            *self.CAMINHOS_WINDOWS,
        ]

        for caminho in candidatos:

            if caminho and os.path.exists(caminho):
                self.configurar(caminho)
                return

    def extrair_texto(self, caminho_imagem):

        """Lê a imagem e devolve o texto reconhecido pelo Tesseract, sem espaços
        nas pontas. Levanta RuntimeError se o Tesseract não estiver instalado.
        """
        imagem = ServicoImagem.carregar(caminho_imagem)

        try:
            texto = pytesseract.image_to_string(
                imagem,
                lang=self._idioma
            )

        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract não encontrado. Instale o Tesseract OCR "
                "(com o idioma português) ou defina a variável de "
                "ambiente TESSERACT_CMD com o caminho do executável."
            ) from None

        return texto.strip()
