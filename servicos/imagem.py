import os
import cv2
import numpy as np

class ServicoImagem:
    """Cuida de ler, melhorar e salvar imagens usando o OpenCV."""

    @staticmethod
    def carregar(caminho):
        """Lê a imagem do disco e devolve como array do OpenCV (colorida).

        Usa numpy + imdecode em vez de cv2.imread porque o imread falha no
        Windows quando o caminho tem acento, como em "Área de Trabalho". Levanta
        FileNotFoundError se o arquivo não existir e ValueError se ele não puder
        ser aberto como imagem.
        """
        caminho = os.fspath(caminho)

        if not os.path.isfile(caminho):
            raise FileNotFoundError(
                "A imagem informada não foi encontrada."
            )
        
        dados = np.fromfile(caminho, dtype=np.uint8)
        imagem = None

        if dados.size > 0:
            try:
                imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)
            except cv2.error:
                imagem = None

        if imagem is None:
            raise ValueError(
                "Não foi possível abrir a imagem."
            )

        return imagem

    @staticmethod
    def salvar(imagem, caminho):
        """Grava a imagem no caminho indicado, criando a pasta se ela não existir.
        A extensão do caminho define o formato (.png se não tiver nenhuma).
        Levanta ValueError se não conseguir codificar a imagem.
        """
        caminho = os.fspath(caminho)

        extensao = os.path.splitext(caminho)[1] or ".png"

        os.makedirs(
            os.path.dirname(caminho) or ".",
            exist_ok=True
        )

        sucesso, buffer = cv2.imencode(extensao, imagem)

        if not sucesso:
            raise ValueError(
                "Não foi possível salvar a imagem melhorada."
            )

        buffer.tofile(caminho)

    @staticmethod
    def melhorar_imagem(caminho_entrada, caminho_saida):
        
        """Deixa a imagem mais fácil de ler para o OCR: reduz o ruído, aumenta a
        nitidez, passa para tons de cinza e melhora o contraste. Lê de
        caminho_entrada, salva em caminho_saida e devolve esse mesmo caminho de
        saída.
        """
        imagem = ServicoImagem.carregar(caminho_entrada)

        # Redução de ruído
        imagem_suave = cv2.GaussianBlur(imagem, (3, 3), 0)

        # Aumento de nitidez
        imagem_nitida = cv2.addWeighted(
            imagem, 1.5,
            imagem_suave, -0.5,
            0
        )

        # Conversão para escala de cinza
        cinza = cv2.cvtColor(imagem_nitida, cv2.COLOR_BGR2GRAY)

        # Melhoria de contraste
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        melhorada = clahe.apply(cinza)

        # Salva a imagem processada
        ServicoImagem.salvar(melhorada, caminho_saida)

        return caminho_saida
