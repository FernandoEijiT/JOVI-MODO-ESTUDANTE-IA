import os

class PDF:
    """Registro de um PDF gerado: onde está o arquivo, de onde veio e qual
    conteúdo o gerou.
    """

    def __init__(self, nome, origem, id_conteudo=None):
        self._nome = nome
        self._origem = origem
        self._id_conteudo = id_conteudo

    @property
    def nome(self):
        return self._nome

    @property
    def origem(self):
        return self._origem

    @property
    def id_conteudo(self):
        return self._id_conteudo

    def exibir(self):
        print(f"PDF: {self._nome}")
        print(f"Origem: {self._origem}")

        if not os.path.exists(self._nome):
            print("⚠️ Arquivo não encontrado no disco.")

    def para_dicionario(self):
        return {
            "nome": self._nome,
            "origem": self._origem,
            "id_conteudo": self._id_conteudo,
        }

    @classmethod
    def de_dicionario(cls, dados):
        return cls(
            str(dados["nome"]),
            str(dados["origem"]),
            dados.get("id_conteudo"),
        )
