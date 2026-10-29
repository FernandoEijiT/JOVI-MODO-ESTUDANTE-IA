class Conteudo:
    """Um conteúdo de estudo: texto digitado ou lido de uma imagem, com resumo
    e a marcação do Modo Estudante.
    """

    def __init__(self, id_conteudo, texto):
        self._id = id_conteudo
        self._texto = texto
        self._resumo = ""
        self._texto_extraido = ""
        self._modo_estudante = False
        self._imagem = ""

    @property
    def id(self):
        return self._id

    @property
    def texto(self):
        return self._texto

    @property
    def resumo(self):
        return self._resumo

    @property
    def texto_extraido(self):
        return self._texto_extraido

    @property
    def modo_estudante(self):
        return self._modo_estudante

    @property
    def imagem(self):
        return self._imagem

    @property
    def texto_principal(self):
        """O texto que representa o conteúdo: o extraído da imagem ou o texto digitado.
        """
        return self._texto_extraido or self._texto

    def editar(self, novo_texto):
        if self._texto_extraido:
            self._texto_extraido = novo_texto
        else:
            self._texto = novo_texto

    def definir_resumo(self, resumo):
        self._resumo = resumo

    def definir_texto_extraido(self, texto):
        self._texto_extraido = texto

    def definir_imagem(self, caminho):
        self._imagem = caminho

    def ativar_modo_estudante(self):
        self._modo_estudante = True

    def desativar_modo_estudante(self):
        self._modo_estudante = False

    def exibir(self):
        print(f"\nID: {self._id}")
        print(f"Conteúdo: {self._texto}")

        if self._imagem:
            print(f"Imagem: {self._imagem}")

        if self._texto_extraido:
            print(f"Texto extraído: {self._texto_extraido}")

        print(f"Resumo: {self._resumo}")

        if self._modo_estudante:
            print("Modo Estudante: Ativado")
        else:
            print("Modo Estudante: Não ativado")

    def para_dicionario(self):
        return {
            "id": self._id,
            "texto": self._texto,
            "resumo": self._resumo,
            "texto_extraido": self._texto_extraido,
            "modo_estudante": self._modo_estudante,
            "imagem": self._imagem,
        }

    @classmethod
    def de_dicionario(cls, dados):
        """Recria o Conteudo a partir do dicionário lido do JSON. Levanta
        KeyError, TypeError ou ValueError se faltar campo ou o tipo estiver
        errado.
        """
        conteudo = cls(int(dados["id"]), str(dados["texto"]))
        conteudo.definir_resumo(str(dados.get("resumo", "")))
        conteudo.definir_texto_extraido(str(dados.get("texto_extraido", "")))
        conteudo.definir_imagem(str(dados.get("imagem", "")))

        if dados.get("modo_estudante"):
            conteudo.ativar_modo_estudante()

        return conteudo
