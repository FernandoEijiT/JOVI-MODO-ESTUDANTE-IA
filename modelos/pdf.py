import os


class PDF:
    """Registro de um PDF gerado: onde o arquivo está, de onde veio o conteúdo e
    qual conteúdo o gerou.
    """

    def __init__(self, nome, origem, id_conteudo=None):
        """Recebe o caminho do arquivo (nome), a origem (texto ou imagem usada) e,
        se quiser, o id do conteúdo que gerou o PDF.
        """
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
        """Imprime o caminho e a origem do PDF, avisando se o arquivo não está mais
        no disco.
        """
        print(f"PDF: {self._nome}")
        print(f"Origem: {self._origem}")

        if not os.path.exists(self._nome):
            print("⚠️ Arquivo não encontrado no disco.")

    def para_dicionario(self):
        """Converte o registro em um dicionário para salvar no JSON."""
        return {
            "nome": self._nome,
            "origem": self._origem,
            "id_conteudo": self._id_conteudo,
        }

    @classmethod
    def de_dicionario(cls, dados):
        """Recria o registro a partir do dicionário lido do JSON e devolve o objeto
        PDF.
        """
        return cls(
            str(dados["nome"]),
            str(dados["origem"]),
            dados.get("id_conteudo"),
        )
