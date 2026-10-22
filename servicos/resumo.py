from configuracao import MODELO_RESUMO

class ServicoResumo:
    # Textos menores que isso são devolvidos como estão
    """Gera resumos automáticos com um modelo do Transformers."""
    MINIMO_PALAVRAS = 30
    # Limite de tokens de entrada do modelo (BART aceita até 1024)
    LIMITE_ENTRADA = 1024

    def __init__(self, modelo=MODELO_RESUMO):

        """Guarda o nome do modelo, mas ainda não o carrega. A carga só acontece
        quando o primeiro resumo for pedido.
        """
        self._nome_modelo = modelo
        self._tokenizador = None
        self._modelo = None

    def _carregar_modelo(self):
       
        """Carrega o tokenizador e o modelo na primeira vez que são necessários.
        Nas chamadas seguintes não faz nada.
        """
        if self._modelo is not None:
            return

        print("\nCarregando modelo de resumo...")
        print("Isso pode demorar na primeira execução...\n")

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self._tokenizador = AutoTokenizer.from_pretrained(
            self._nome_modelo
        )

        self._modelo = AutoModelForSeq2SeqLM.from_pretrained(
            self._nome_modelo
        )

        self._modelo.eval()

    def gerar_resumo(self, texto):

        """Resume o texto e devolve o resumo. Texto vazio devolve uma string vazia,
        e textos com menos de MINIMO_PALAVRAS palavras voltam do jeito que
        vieram, porque não compensa resumir.
        """
        if not texto or texto.strip() == "":
            return ""

        palavras = texto.split()

        if len(palavras) < self.MINIMO_PALAVRAS:
            return texto.strip()

        self._carregar_modelo()

        tamanho = len(palavras)

        max_length = min(100, max(30, tamanho // 2))
        min_length = min(30, max_length - 5)

        entradas = self._tokenizador(
            texto,
            return_tensors="pt",
            truncation=True,
            max_length=self.LIMITE_ENTRADA
        )

        ids_resumo = self._modelo.generate(
            **entradas,
            max_length=max_length,
            min_length=min_length,
            do_sample=False
        )

        return self._tokenizador.decode(
            ids_resumo[0],
            skip_special_tokens=True
        ).strip()
