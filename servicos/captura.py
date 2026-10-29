import unicodedata
from configuracao import EXTENSOES_IMAGEM

class ServicoCaptura:
    """Validações e tratamentos simples para o que o usuário digita."""

    @staticmethod
    def validar_conteudo(texto):
        return bool(texto and texto.strip())

    @staticmethod
    def limpar_caminho(texto):
        # Tira espaços e aspas.
        if not texto:
            return ""
        return texto.strip().strip("\"'").strip()

    @staticmethod
    def eh_imagem(caminho):
        return caminho.lower().endswith(EXTENSOES_IMAGEM)

    @staticmethod
    def normalizar_texto(texto):
        """Deixa o texto em minúsculas e sem acentos."""
        if not texto:
            return ""
        decomposto = unicodedata.normalize("NFD", texto.lower())

        return "".join(
            caractere
            for caractere in decomposto
            if not unicodedata.combining(caractere)
        )

    @staticmethod
    def extensoes_imagem():
        return EXTENSOES_IMAGEM
