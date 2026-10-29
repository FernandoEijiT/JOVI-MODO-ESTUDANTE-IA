import os
import cv2
import numpy as np

class ServicoImagem:
    """Lê, melhora e salva imagens usando o OpenCV."""

    @staticmethod
    def carregar(caminho):
        """Lê a imagem do disco e devolve como array do OpenCV. Levanta
        FileNotFoundError se o arquivo não existir e ValueError se não puder
        ser aberto como imagem.
        """
        caminho = os.fspath(caminho)

        if not os.path.isfile(caminho):
            raise FileNotFoundError("A imagem informada não foi encontrada.")

        dados = np.fromfile(caminho, dtype=np.uint8)
        imagem = None

        if dados.size > 0:
            try:
                imagem = cv2.imdecode(dados, cv2.IMREAD_COLOR)
            except cv2.error:
                imagem = None

        if imagem is None:
            raise ValueError("Não foi possível abrir a imagem.")

        return imagem

    @staticmethod
    def salvar(imagem, caminho):
        caminho = os.fspath(caminho)

        extensao = os.path.splitext(caminho)[1] or ".png"

        os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)

        sucesso, buffer = cv2.imencode(extensao, imagem)

        if not sucesso:
            raise ValueError("Não foi possível salvar a imagem melhorada.")

        buffer.tofile(caminho)

    @staticmethod
    def melhorar_imagem(caminho_entrada, caminho_saida):
        """Prepara a imagem para o OCR,
        salva em caminho_saida e devolve esse caminho.
        """
        imagem = ServicoImagem.carregar(caminho_entrada)

        # Redução de ruído
        imagem_suave = cv2.GaussianBlur(imagem, (3, 3), 0)

        # Aumento de nitidez
        imagem_nitida = cv2.addWeighted(imagem, 1.5, imagem_suave, -0.5, 0)

        # Contraste e nitidez mantendo as cores
        melhorada = imagem_nitida

        ServicoImagem.salvar(melhorada, caminho_saida)

        return caminho_saida
