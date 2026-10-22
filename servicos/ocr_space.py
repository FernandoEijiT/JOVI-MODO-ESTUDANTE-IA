import cv2
import requests
from configuracao import IDIOMA_OCR, OCR_SPACE_API_KEY
from servicos.imagem import ServicoImagem

class ServicoOCRSpace:
    """OCR por API externa: envia a imagem para o OCR.space e recebe o texto
    reconhecido.
    """

    URL = "https://api.ocr.space/parse/image"

    # Limite de tamanho do arquivo no plano gratuito (1 MB)
    LIMITE_BYTES = 1024 * 1024

    def __init__(self, chave_api=None, idioma=IDIOMA_OCR, engine=2):
        """Cria o serviço. Chave da API, idioma e versão do motor de OCR são
        opcionais; sem chave, usa a do arquivo .env.
        """
        self._chave = (chave_api or OCR_SPACE_API_KEY or "").strip()
        self._idioma = idioma
        self._engine = engine

    @property
    def configurado(self):
        """Devolve True se existe uma chave de API configurada."""
        return bool(self._chave)

    def _preparar_imagem(self, caminho):
        """Converte a imagem para JPEG e vai diminuindo o tamanho até caber no
        limite de 1 MB do plano gratuito. Devolve os bytes prontos para enviar.
        """
        imagem = ServicoImagem.carregar(caminho)

        while True:
            _, buffer = cv2.imencode(
                ".jpg",
                imagem,
                [cv2.IMWRITE_JPEG_QUALITY, 85]
            )

            if buffer.nbytes <= self.LIMITE_BYTES:
                return buffer.tobytes()

            imagem = cv2.resize(
                imagem,
                None,
                fx=0.8,
                fy=0.8,
                interpolation=cv2.INTER_AREA
            )

    def extrair_texto(self, caminho_imagem):

        """Envia a imagem para a API e devolve o texto reconhecido, com as quebras
        de linha padronizadas. Levanta RuntimeError se faltar a chave, se a
        conexão falhar ou se a API retornar erro.
        """
        if not self.configurado:
            raise RuntimeError(
                "Chave da API do OCR.space não configurada. "
                "Defina OCR_SPACE_API_KEY no arquivo .env."
            )

        conteudo = self._preparar_imagem(caminho_imagem)

        try:
            resposta = requests.post(
                self.URL,
                headers={"apikey": self._chave},
                files={"file": ("imagem.jpg", conteudo)},
                data={
                    "language": self._idioma,
                    "OCREngine": self._engine,
                    "scale": "true",
                    "detectOrientation": "true",
                },
                timeout=60
            )

            resposta.raise_for_status()

            dados = resposta.json()

        except (requests.RequestException, ValueError) as erro:
            raise RuntimeError(
                f"Falha ao acessar a API do OCR.space: {erro}"
            ) from None

        if dados.get("IsErroredOnProcessing"):

            mensagem = dados.get("ErrorMessage")

            if isinstance(mensagem, list):
                mensagem = " ".join(mensagem)

            raise RuntimeError(
                f"O OCR.space retornou um erro: {mensagem}"
            )

        resultados = dados.get("ParsedResults") or []

        texto = "\n".join(
            resultado.get("ParsedText", "")
            for resultado in resultados
        )

        # A API usa quebras de linha do Windows (\r\n); padroniza para \n
        return texto.replace("\r\n", "\n").replace("\r", "\n").strip()
