class Conteudo:
    """Guarda um conteúdo de estudo: o texto digitado ou o que foi lido de uma
    imagem, mais o resumo e se o Modo Estudante está ativo.
    """

    def __init__(self, id_conteudo, texto):
        """Cria o conteúdo com um id e o texto inicial. Quando o conteúdo vem de
        uma imagem, esse texto é o caminho do arquivo. Resumo e demais campos
        começam vazios.
        """
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
        """Devolve o texto que de fato representa o conteúdo: o extraído da imagem,
        se houver, ou o texto digitado.
        """
        return self._texto_extraido or self._texto

    def editar(self, novo_texto):
        """Troca o texto do conteúdo por novo_texto (que já deve ter sido
        validado). Se o conteúdo veio de uma imagem, quem muda é o texto
        extraído pelo OCR; senão, o texto digitado.
        """
        if self._texto_extraido:
            self._texto_extraido = novo_texto
        else:
            self._texto = novo_texto

    def definir_resumo(self, resumo):
        """Guarda o resumo (str) do conteúdo."""
        self._resumo = resumo

    def definir_texto_extraido(self, texto):
        """Guarda o texto (str) que o OCR leu da imagem."""
        self._texto_extraido = texto

    def definir_imagem(self, caminho):
        """Guarda o caminho (str) da imagem de origem."""
        self._imagem = caminho

    def ativar_modo_estudante(self):
        """Marca o conteúdo como Modo Estudante ativado."""
        self._modo_estudante = True

    def desativar_modo_estudante(self):
        """Tira a marcação de Modo Estudante do conteúdo."""
        self._modo_estudante = False

    def exibir(self):
        """Imprime no terminal os dados do conteúdo: id, texto, imagem e texto
        extraído (quando houver), resumo e se o Modo Estudante está ativo.
        """
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
        """Transforma o conteúdo em um dicionário simples, pronto para ir para o
        JSON.
        """
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
        """Faz o caminho inverso de para_dicionario: recebe o dicionário lido do
        JSON e devolve o objeto Conteudo. Se faltar algum campo obrigatório ou o
        tipo estiver errado, levanta KeyError, TypeError ou ValueError.
        """
        conteudo = cls(int(dados["id"]), str(dados["texto"]))
        conteudo.definir_resumo(str(dados.get("resumo", "")))
        conteudo.definir_texto_extraido(str(dados.get("texto_extraido", "")))
        conteudo.definir_imagem(str(dados.get("imagem", "")))

        if dados.get("modo_estudante"):
            conteudo.ativar_modo_estudante()

        return conteudo
