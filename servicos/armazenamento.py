import json
import os
from configuracao import ARQUIVO_DADOS
from modelos.conteudo import Conteudo
from modelos.pdf import PDF

class ServicoArmazenamento:
    """Salva e carrega os conteúdos e PDFs em um arquivo JSON."""

    @staticmethod
    def salvar(conteudos, pdfs, caminho=ARQUIVO_DADOS):
        """Grava as listas no JSON. Escreve primeiro num arquivo temporário e só
        depois troca pelo definitivo. Levanta RuntimeError se não conseguir gravar.
        """
        dados = {
            "conteudos": [conteudo.para_dicionario() for conteudo in conteudos],
            "pdfs": [pdf.para_dicionario() for pdf in pdfs],
        }

        caminho = os.fspath(caminho)
        temporario = caminho + ".tmp"

        try:
            os.makedirs(os.path.dirname(caminho) or ".", exist_ok=True)

            with open(temporario, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo, ensure_ascii=False, indent=4)

            os.replace(temporario, caminho)

        except OSError as erro:
            raise RuntimeError(
                f"Não foi possível salvar os dados: {erro}"
            ) from None

    @staticmethod
    def carregar(caminho=ARQUIVO_DADOS):
        """Lê o JSON e devolve a lista de conteúdos e a de PDFs. Se o arquivo estiver quebrado, ele é renomeado para
        .corrompido e o método levanta ValueError. Levanta RuntimeError se o
        arquivo não puder ser lido.
        """
        caminho = os.fspath(caminho)

        if not os.path.isfile(caminho):
            return [], []

        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                dados = json.load(arquivo)

            conteudos = [
                Conteudo.de_dicionario(item) for item in dados["conteudos"]
            ]
            pdfs = [PDF.de_dicionario(item) for item in dados["pdfs"]]

        except (json.JSONDecodeError, KeyError, TypeError, ValueError):
            backup = caminho + ".corrompido"
            try:
                os.replace(caminho, backup)
            except OSError:
                backup = caminho

            raise ValueError(
                "O arquivo de dados estava inválido e foi guardado em "
                f"'{backup}'. O programa vai iniciar sem conteúdos salvos."
            ) from None

        except OSError as erro:
            raise RuntimeError(
                f"Não foi possível ler os dados salvos: {erro}"
            ) from None

        return conteudos, pdfs
