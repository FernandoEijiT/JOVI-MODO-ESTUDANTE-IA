import re

from servicos.captura import ServicoCaptura


class ServicoDocumento:
    """Tenta descobrir se um texto parece um documento, procurando palavras-chave."""

    PALAVRAS_CHAVE = (
        "titulo",
        "capitulo",
        "introducao",
        "introducoes",
        "resumo",
        "conclusao",
        "conclusoes",
        "referencia",
    )

    # \b no início: a palavra precisa COMEÇAR com a palavra-chave, então
    # "titulos", "capitulo3" e "introducoes" disparam, mas "subtitulo" e
    # "preferencia" não.
    _PADRAO = re.compile(r"\b(?:" + "|".join(PALAVRAS_CHAVE) + r")")

    @staticmethod
    def detectar_documento(texto):
        """Procura no texto palavras como título, capítulo, introdução, resumo,
        conclusão e referência.

        Ignora maiúsculas e acentos, e a palavra do texto precisa começar com a
        palavra-chave (então "títulos" vale, mas "subtítulo" não). Devolve True
        se achar alguma e False se não achar ou se o texto for vazio.
        """
        if not texto:
            return False

        texto = ServicoCaptura.normalizar_texto(texto)

        return ServicoDocumento._PADRAO.search(texto) is not None
