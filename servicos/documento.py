import re
from servicos.captura import ServicoCaptura

class ServicoDocumento:
    """Tenta descobrir se um texto parece material de estudo ou um documento,
    procurando palavras-chave.
    """

    # A palavra do texto precisa começar com uma destas.
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

    # Estas precisam aparecer inteiras.
    PALAVRAS_ESTUDO = (
        "aula", "aulas",
        "materia", "materias",
        "exercicio", "exercicios",
        "conceito", "conceitos",
        "definicao", "definicoes",
        "teorema", "teoremas",
        "formula", "formulas",
        "prova", "provas",
        "disciplina", "disciplinas",
        "estudo", "estudos",
        "licao", "licoes",
        "apostila", "apostilas",
        "questao", "questoes",
    )

    _PADRAO = re.compile(
        r"\b(?:" + "|".join(PALAVRAS_CHAVE) + r")"
        r"|\b(?:" + "|".join(PALAVRAS_ESTUDO) + r")\b"
    )

    @staticmethod
    def detectar_documento(texto):
        """Devolve True se o texto tiver alguma palavra de documento ou de estudo
        (título, capítulo, resumo, aula, prova, conceito...).
        """
        if not texto:
            return False

        texto = ServicoCaptura.normalizar_texto(texto)

        return ServicoDocumento._PADRAO.search(texto) is not None
