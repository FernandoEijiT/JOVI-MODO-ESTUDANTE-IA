import unicodedata
from configuracao import EXTENSOES_IMAGEM

class ServicoCaptura:
    """Validações e tratamentos simples para o que o usuário digita."""

    @staticmethod
    def validar_conteudo(texto):
        """Confere se o usuário digitou alguma coisa. Recebe o texto e devolve True
        se houver algo além de espaços, ou False se estiver vazio.
        """
        return bool(texto and texto.strip())

    @staticmethod
    def limpar_caminho(texto):
        """Tira espaços e aspas das pontas de um caminho (comum quando o arquivo é
        arrastado para o terminal). Devolve o caminho limpo, ou uma string vazia
        se não vier nada.
        """
        if not texto:
            return ""
        return texto.strip().strip("\"'").strip()

    @staticmethod
    def eh_imagem(caminho):
        """Diz se o caminho termina com uma extensão de imagem aceita (as de
        EXTENSOES_IMAGEM). Devolve True ou False.
        """
        return caminho.lower().endswith(EXTENSOES_IMAGEM)

    @staticmethod
    def normalizar_texto(texto):
        """Deixa o texto em minúsculas e sem acentos, para que buscas e comparações
        não dependam disso. Devolve uma string vazia se o texto for vazio.
        """
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
        """Devolve a tupla com as extensões de imagem aceitas, como .jpg e .png."""
        return EXTENSOES_IMAGEM
