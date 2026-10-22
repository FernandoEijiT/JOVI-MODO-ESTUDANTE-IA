import os

from configuracao import OCR_PROVEDOR, PASTA_IMAGENS
from modelos.conteudo import Conteudo
from modelos.pdf import PDF
from servicos.armazenamento import ServicoArmazenamento
from servicos.captura import ServicoCaptura
from servicos.documento import ServicoDocumento
from servicos.imagem import ServicoImagem
from servicos.ocr import ServicoOCR
from servicos.ocr_space import ServicoOCRSpace
from servicos.pdf import ServicoPDF
from servicos.resumo import ServicoResumo

TITULO_PDF = "Modo Estudante - JOVI"


class ModoEstudante:
    """Controla o menu e o fluxo principal do Modo Estudante."""

    def __init__(self):
        """Prepara os serviços (resumo e OCR) e carrega os dados salvos na última
        execução, se houver.
        """
        self._conteudos = []
        self._pdfs = []
        self._servico_resumo = ServicoResumo()
        # OCR local (Tesseract) e, opcionalmente, a API externa OCR.space
        self._servico_ocr = ServicoOCR()
        self._servico_ocr_api = (
            ServicoOCRSpace() if OCR_PROVEDOR == "ocrspace" else None
        )
        self._proximo_id = 1

        self._carregar_dados()

    # ------------------------------------------------------------------
    # Persistência
    # ------------------------------------------------------------------

    def _carregar_dados(self):
        """Lê o JSON salvo e ajusta o próximo id para não repetir os que já foram
        usados. Se o arquivo estiver inválido ou não puder ser lido, mostra um
        aviso e começa vazio.
        """
        try:
            self._conteudos, self._pdfs = ServicoArmazenamento.carregar()

        except (ValueError, RuntimeError) as erro:
            print(f"\n⚠️ {erro}")
            return

        self._proximo_id = max(
            (conteudo.id for conteudo in self._conteudos),
            default=0
        ) + 1

        if self._conteudos:
            print(
                f"\n💾 {len(self._conteudos)} conteúdo(s) e "
                f"{len(self._pdfs)} PDF(s) carregado(s) da última sessão."
            )

    def _salvar_dados(self):
        """Grava o estado atual no JSON. Se não conseguir, apenas avisa o usuário e
        o programa continua.
        """
        try:
            ServicoArmazenamento.salvar(self._conteudos, self._pdfs)

        except RuntimeError as erro:
            print(f"\n⚠️ {erro}")

    # ------------------------------------------------------------------
    # Menu e entradas
    # ------------------------------------------------------------------

    def exibir_menu(self):
        """Mostra o menu e devolve a opção digitada, sem espaços nas pontas."""
        print("\n====================================")
        print("        MODO ESTUDANTE - JOVI")
        print("====================================")

        print("1 - Capturar conteúdo")
        print("2 - Ver conteúdos")
        print("3 - Buscar conteúdo")
        print("4 - Editar conteúdo")
        print("5 - Remover conteúdo")
        print("6 - Processar imagem / OCR")
        print("7 - Gerar PDF")
        print("8 - Ver PDFs gerados")
        print("9 - Sobre o projeto")
        print("0 - Sair")

        return input("\nEscolha uma opção: ").strip()

    @staticmethod
    def _perguntar_sim_nao(pergunta):
        """Faz a pergunta e repete até a pessoa responder sim ou não. Devolve True
        para sim e False para não.
        """
        while True:
            resposta = input(f"\n{pergunta} (sim/não): ").lower().strip()

            if resposta in ("sim", "s"):
                return True

            if resposta in ("não", "nao", "n"):
                return False

            print("\n⚠️ Resposta inválida. Digite sim ou não.")

    def _novo_conteudo(self, texto):
        """Cria um Conteudo com o próximo id livre e avança o contador. O conteúdo
        ainda não entra na lista; quem chamou é que faz isso.
        """
        conteudo = Conteudo(self._proximo_id, texto)

        self._proximo_id += 1

        return conteudo

    def _selecionar_conteudo(self):
        """Pede um id ao usuário e devolve o conteúdo correspondente. Devolve None
        (e avisa o motivo) se a lista estiver vazia, se o que foi digitado não
        for um número ou se não existir conteúdo com esse id.
        """
        if not self._conteudos:
            print("\n⚠️ Nenhum conteúdo salvo.")
            return None

        try:
            id_conteudo = int(input("\nDigite o ID do conteúdo: "))

        except ValueError:
            print("\n⚠️ ID inválido.")
            return None

        for conteudo in self._conteudos:

            if conteudo.id == id_conteudo:
                return conteudo

        print("\n⚠️ Conteúdo não encontrado.")

        return None

    # ------------------------------------------------------------------
    # Serviços auxiliares
    # ------------------------------------------------------------------

    def _extrair_texto(self, caminho_imagem):
        """Lê o texto da imagem pela API OCR.space e, se ela falhar, usa o
        Tesseract local. Recebe o caminho da imagem já melhorada e devolve o
        texto reconhecido.
        """
        if self._servico_ocr_api is not None:

            try:
                print("🌐 Extraindo texto com a API OCR.space...")

                return self._servico_ocr_api.extrair_texto(caminho_imagem)

            except RuntimeError as erro:
                print(f"\n⚠️ {erro}")
                print("Usando o Tesseract local como alternativa...")

        else:
            print("💻 Extraindo texto com o Tesseract local...")

        return self._servico_ocr.extrair_texto(caminho_imagem)

    def _gerar_resumo(self, conteudo, texto):
        """Gera o resumo do texto e guarda no conteúdo. Se o resumo falhar por
        qualquer motivo, mostra o aviso e deixa o resumo vazio.
        """
        try:
            resumo = self._servico_resumo.gerar_resumo(texto)

        except Exception as erro:
            print(f"\n⚠️ Não foi possível gerar o resumo: {erro}")
            resumo = ""

        conteudo.definir_resumo(resumo)

    def _oferecer_modo_estudante(self, conteudo, texto):
        """Pergunta se o usuário quer ativar o Modo Estudante para o conteúdo
        recém-criado. A pergunta aparece sempre; se o texto parecer um
        documento, um aviso é mostrado antes. Devolve True se o modo foi
        ativado.
        """
        if ServicoDocumento.detectar_documento(texto):
            print("\n📄 Possível documento detectado!")

        if self.ativar_modo_estudante():
            conteudo.ativar_modo_estudante()
            return True

        return False

    def _pdfs_do_conteudo(self, conteudo):
        """Devolve a lista de PDFs já gerados a partir do conteúdo."""
        return [
            pdf for pdf in self._pdfs if pdf.id_conteudo == conteudo.id
        ]

    def _exportar_pdf(self, conteudo):
        """Gera o PDF do conteúdo (com o texto principal e o resumo), registra o
        arquivo e salva os dados. Se o PDF já existia, o arquivo é sobrescrito e
        o registro não é duplicado. Devolve o caminho do PDF.
        """
        origem = conteudo.imagem or conteudo.texto

        caminho = ServicoPDF.gerar_pdf(
            f"conteudo_{conteudo.id}.pdf",
            TITULO_PDF,
            conteudo.texto_principal,
            conteudo.resumo
        )

        # Gerar o PDF do mesmo conteúdo de novo não duplica o registro
        if not any(pdf.nome == caminho for pdf in self._pdfs):
            self._pdfs.append(PDF(caminho, origem, conteudo.id))

        self._salvar_dados()

        return caminho

    # ------------------------------------------------------------------
    # Funcionalidades do menu
    # ------------------------------------------------------------------

    def ativar_modo_estudante(self):
        """Pergunta se o usuário quer ativar o Modo Estudante. Devolve True se ele
        confirmou.
        """
        if self._perguntar_sim_nao("Ativar Modo Estudante?"):
            print("\n🚀 Modo Estudante ativado!")
            return True

        print("\nModo Estudante não foi ativado.")

        return False

    def capturar_conteudo(self):
        """Pede um texto ou o caminho de uma imagem. Se for imagem, segue para o
        processamento; se for texto, gera o resumo, pergunta sobre o Modo
        Estudante e salva.
        """
        entrada = input(
            "\nDigite o conteúdo ou caminho da imagem: "
        ).strip()

        if not ServicoCaptura.validar_conteudo(entrada):
            print("\n⚠️ Conteúdo inválido!")
            return

        # Verifica se é uma imagem
        caminho = ServicoCaptura.limpar_caminho(entrada)

        if ServicoCaptura.eh_imagem(caminho):
            self._processar_caminho(caminho)
            return

        # Conteúdo de texto
        conteudo = self._novo_conteudo(entrada)

        self._gerar_resumo(conteudo, entrada)
        self._oferecer_modo_estudante(conteudo, entrada)

        self._conteudos.append(conteudo)
        self._salvar_dados()

        print("\n✅ Conteúdo salvo com sucesso!")
        print(f"ID: {conteudo.id}")
        print(f"Resumo: {conteudo.resumo}")

    def solicitar_imagem(self):
        """Pede o caminho de uma imagem e a processa. Recusa caminho vazio e
        arquivos que não tenham uma extensão de imagem aceita.
        """
        caminho = ServicoCaptura.limpar_caminho(
            input("\nDigite o caminho da imagem: ")
        )

        if not ServicoCaptura.validar_conteudo(caminho):
            print("\n⚠️ Caminho inválido.")
            return

        if not ServicoCaptura.eh_imagem(caminho):
            extensoes = ", ".join(ServicoCaptura.extensoes_imagem())
            print(f"\n⚠️ Formato não suportado. Use: {extensoes}")
            return

        self._processar_caminho(caminho)

    def _processar_caminho(self, caminho):
        """Recebe o caminho da imagem, confere se o arquivo existe e, se existir,
        manda processar.
        """
        if not os.path.exists(caminho):
            print("\n⚠️ A imagem não foi encontrada.")
            return

        self.processar_imagem(caminho)

    def processar_imagem(self, caminho_imagem):
        """Faz o fluxo completo da imagem: melhora a imagem, extrai o texto por
        OCR, gera o resumo, pergunta sobre o Modo Estudante, salva e oferece
        gerar o PDF.

        Recebe o caminho de uma imagem que já existe. Erros de arquivo, OCR ou
        gravação aparecem na tela em vez de derrubar o programa.
        """
        print("\n🖼️ Processando imagem...")

        nome_sem_extensao = os.path.splitext(
            os.path.basename(caminho_imagem)
        )[0]

        caminho_melhorado = PASTA_IMAGENS / f"{nome_sem_extensao}_melhorada.png"

        try:

            # Melhora a imagem
            ServicoImagem.melhorar_imagem(
                caminho_imagem,
                caminho_melhorado
            )

            print("✅ Imagem melhorada com OpenCV.")

            # OCR
            texto_extraido = self._extrair_texto(caminho_melhorado)

            if not texto_extraido:
                print("\n⚠️ Nenhum texto foi identificado na imagem.")
                return

            print("\n===== TEXTO EXTRAÍDO =====")
            print(texto_extraido)

            # Cria o conteúdo
            conteudo = self._novo_conteudo(caminho_imagem)
            conteudo.definir_imagem(caminho_imagem)
            conteudo.definir_texto_extraido(texto_extraido)

            self._gerar_resumo(conteudo, texto_extraido)
            self._oferecer_modo_estudante(conteudo, texto_extraido)

            self._conteudos.append(conteudo)
            self._salvar_dados()

            print("\n✅ Imagem processada e conteúdo salvo!")
            print(f"ID: {conteudo.id}")

            # Gera PDF
            if self._perguntar_sim_nao("Deseja gerar um PDF?"):

                caminho_pdf = self._exportar_pdf(conteudo)

                print(f"\n📄 PDF gerado: {caminho_pdf}")

        except (FileNotFoundError, ValueError, RuntimeError, OSError) as erro:
            print(f"\n❌ Erro durante o processamento: {erro}")

    def visualizar_conteudos(self):
        """Lista todos os conteúdos salvos, numerados na ordem em que aparecem."""
        if not self._conteudos:
            print("\n⚠️ Nenhum conteúdo salvo.")
            return

        print("\n===== CONTEÚDOS CAPTURADOS =====")

        total = len(self._conteudos)

        for posicao, conteudo in enumerate(self._conteudos, start=1):
            print(f"\n--- Conteúdo {posicao} de {total} ---", end="")
            conteudo.exibir()

    def buscar_conteudo(self):
        """Pede um termo e mostra os conteúdos que o têm no texto, no texto
        extraído ou no resumo. A busca ignora maiúsculas e acentos.
        """
        if not self._conteudos:
            print("\n⚠️ Nenhum conteúdo salvo.")
            return

        termo = ServicoCaptura.normalizar_texto(
            input("\nDigite o termo que deseja buscar: ").strip()
        )

        if termo == "":
            print("\n⚠️ Informe um termo.")
            return

        encontrados = [
            conteudo
            for conteudo in self._conteudos
            if termo in ServicoCaptura.normalizar_texto(
                f"{conteudo.texto} {conteudo.texto_extraido} {conteudo.resumo}"
            )
        ]

        if not encontrados:
            print("\n⚠️ Nenhum conteúdo encontrado.")
            return

        print(f"\n===== RESULTADOS ({len(encontrados)}) =====")

        for conteudo in encontrados:
            conteudo.exibir()

    def editar_conteudo(self):
        """Pede um id e um novo texto, atualiza o conteúdo e refaz o resumo. Se já
        existir PDF desse conteúdo, avisa que é preciso gerá-lo de novo.
        """
        conteudo = self._selecionar_conteudo()

        if conteudo is None:
            return

        print(f"\nTexto atual: {conteudo.texto_principal}")

        novo_texto = input("\nDigite o novo conteúdo: ").strip()

        if not ServicoCaptura.validar_conteudo(novo_texto):
            print("\n⚠️ Conteúdo inválido.")
            return

        conteudo.editar(novo_texto)

        self._gerar_resumo(conteudo, novo_texto)
        self._salvar_dados()

        print("\n✅ Conteúdo editado com sucesso!")

        if self._pdfs_do_conteudo(conteudo):
            print("ℹ️ Gere o PDF novamente (opção 7) para atualizar o arquivo.")

    def remover_conteudo(self):
        """Pede um id e, depois da confirmação, apaga o conteúdo e também os PDFs
        gerados a partir dele.
        """
        conteudo = self._selecionar_conteudo()

        if conteudo is None:
            return

        if not self._perguntar_sim_nao("Tem certeza que deseja remover?"):
            print("\nOperação cancelada.")
            return

        for pdf in self._pdfs_do_conteudo(conteudo):

            try:
                os.remove(pdf.nome)

            except FileNotFoundError:
                pass

            except OSError as erro:
                print(f"\n⚠️ Não foi possível apagar {pdf.nome}: {erro}")

            self._pdfs.remove(pdf)

        self._conteudos.remove(conteudo)
        self._salvar_dados()

        print("\n🗑️ Conteúdo removido com sucesso!")

    def gerar_pdf_conteudo(self):
        """Pede um id e gera o PDF desse conteúdo, mostrando onde o arquivo foi
        salvo.
        """
        conteudo = self._selecionar_conteudo()

        if conteudo is None:
            return

        try:
            caminho = self._exportar_pdf(conteudo)

        except (OSError, ValueError) as erro:
            print(f"\n❌ Erro ao gerar o PDF: {erro}")
            return

        print("\n✅ PDF gerado com sucesso!")
        print(f"📄 Arquivo: {caminho}")

    def visualizar_pdfs(self):
        """Lista os PDFs gerados, numerados, com o caminho e a origem de cada um."""
        if not self._pdfs:
            print("\n⚠️ Nenhum PDF gerado.")
            return

        print("\n===== PDFs GERADOS =====")

        for indice, pdf in enumerate(self._pdfs, start=1):

            print(f"\n{indice} - ")

            pdf.exibir()

    def sobre_projeto(self):
        """Mostra uma explicação curta do projeto e das tecnologias usadas."""
        print("\n===== SOBRE O PROJETO =====")

        print(
            "O Modo Estudante IA é uma proposta "
            "para auxiliar estudantes."
        )

        print(
            "O sistema processa imagens, extrai textos "
            "e gera resumos."
        )

        print(
            "Também permite organizar conteúdos, gerar PDFs "
            "e guarda tudo em JSON entre uma execução e outra."
        )

        print(
            "A solução utiliza Python, OpenCV, "
            "OCR, Transformers e ReportLab."
        )

    def executar(self):
        """Roda o loop principal: mostra o menu, chama a ação escolhida e volta ao
        menu. Só termina com a opção 0 ou com Ctrl+C / Ctrl+D.
        """
        acoes = {
            "1": self.capturar_conteudo,
            "2": self.visualizar_conteudos,
            "3": self.buscar_conteudo,
            "4": self.editar_conteudo,
            "5": self.remover_conteudo,
            "6": self.solicitar_imagem,
            "7": self.gerar_pdf_conteudo,
            "8": self.visualizar_pdfs,
            "9": self.sobre_projeto,
        }

        try:

            while True:

                opcao = self.exibir_menu()

                if opcao == "0":
                    print("\n👋 Encerrando o programa...")
                    break

                acao = acoes.get(opcao)

                if acao is None:
                    print("\n❌ Opção inválida!")
                    continue

                acao()

        except (KeyboardInterrupt, EOFError):
            # Ctrl+C / Ctrl+D encerram o programa sem mostrar erro
            print("\n\n👋 Encerrando o programa...")
