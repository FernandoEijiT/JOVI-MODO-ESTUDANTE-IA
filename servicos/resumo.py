import re
from collections import Counter
from configuracao import MODELO_RESUMO, RESUMO_PROVEDOR, TOKENIZADOR_RESUMO

class ServicoResumo:
    """Gera resumos com um modelo do Transformers. Se o modelo não puder ser
    carregado, usa um resumo simples por frases para o programa continuar funcionando.
    """
    
    MINIMO_PALAVRAS = 30

    LIMITE_ENTRADA = 512

    FRASES_RESUMO = 3

    def __init__(self, modelo=MODELO_RESUMO, tokenizador=TOKENIZADOR_RESUMO):
        self._nome_modelo = modelo
        self._nome_tokenizador = tokenizador
        self._tokenizador = None
        self._modelo = None
        self._usar_modelo = RESUMO_PROVEDOR != "simples"

    def _carregar_modelo(self):
        if self._modelo is not None:
            return

        print("\nCarregando modelo de resumo...")
        print("Isso pode demorar na primeira execução...\n")

        from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

        self._tokenizador = AutoTokenizer.from_pretrained(
            self._nome_tokenizador,
            use_fast=False
        )

        self._modelo = AutoModelForSeq2SeqLM.from_pretrained(
            self._nome_modelo
        )

        self._modelo.eval()

    def gerar_resumo(self, texto):
        """Resume o texto. Texto vazio devolve string vazia e texto curto volta
        como está. Usa o modelo de IA e, se ele não carregar, o resumo simples.
        """
        if not texto or not texto.strip():
            return ""

        palavras = texto.split()

        if len(palavras) < self.MINIMO_PALAVRAS:
            return texto.strip()

        if self._usar_modelo:
            try:
                self._carregar_modelo()

            except (ImportError, OSError, ValueError) as erro:
                print(f"\n⚠️ Modelo de resumo indisponível: {erro}")
                print("Usando o resumo simples por frases...")
                self._usar_modelo = False

        if self._usar_modelo:
            return self._resumo_modelo(texto, len(palavras))

        return self._resumo_simples(texto)

    def _resumo_modelo(self, texto, qtd_palavras):
        max_length = min(120, max(40, qtd_palavras // 2))
        min_length = min(30, max_length - 10)

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
            num_beams=4,
            no_repeat_ngram_size=3,
            early_stopping=True,
            do_sample=False
        )

        return self._tokenizador.decode(
            ids_resumo[0],
            skip_special_tokens=True
        ).strip()

    @staticmethod
    def _palavras(texto):
        return [palavra.lower() for palavra in re.findall(r"[^\W\d_]{5,}", texto)]

    def _resumo_simples(self, texto):
        """Escolhe as frases com as palavras mais frequentes do texto e as
        devolve na ordem em que aparecem.
        """
        frases = [
            frase.strip()
            for frase in re.split(r"(?<=[.!?])\s+|\n+", texto)
            if len(frase.split()) >= 5
        ]

        if len(frases) <= self.FRASES_RESUMO:
            return " ".join(frases) or texto.strip()

        frequencia = Counter(self._palavras(texto))

        pontuacao = [
            sum(frequencia[palavra] for palavra in set(self._palavras(frase)))
            for frase in frases
        ]

        melhores = sorted(
            range(len(frases)),
            key=lambda posicao: pontuacao[posicao],
            reverse=True
        )[:self.FRASES_RESUMO]

        return " ".join(frases[posicao] for posicao in sorted(melhores))
