import os
import shutil
import pytesseract
from configuracao import IDIOMA_OCR
from servicos.imagem import ServicoImagem

class ServicoOCR:
    """OCR local: lê o texto das imagens com o Tesseract instalado no PC."""

    # Local onde o executável costuma ficar
    CAMINHOS_WINDOWS = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    )

    def __init__(self, idioma=IDIOMA_OCR):
        self._idioma = idioma
        self._configurado = False

        self._configurar_automaticamente()

    @property
    def configurado(self):
        return self._configurado

    def configurar(self, caminho_tesseract):
        if not os.path.exists(caminho_tesseract):
            raise FileNotFoundError("O caminho do Tesseract não foi encontrado.")

        pytesseract.pytesseract.tesseract_cmd = caminho_tesseract

        self._configurado = True

    def _configurar_automaticamente(self):
        # Procura em TESSERACT_CMD, no PATH e nas pastas padrão do Windows
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
        """Devolve o texto reconhecido pelo Tesseract. Levanta RuntimeError se
        ele não estiver instalado.
        """
        imagem = ServicoImagem.carregar(caminho_imagem)

        try:
            texto = pytesseract.image_to_string(imagem, lang=self._idioma)

        except pytesseract.TesseractNotFoundError:
            raise RuntimeError(
                "Tesseract não encontrado. Instale o Tesseract OCR "
                "(com o idioma português) ou defina a variável de "
                "ambiente TESSERACT_CMD com o caminho do executável."
            ) from None

        return texto.strip()
