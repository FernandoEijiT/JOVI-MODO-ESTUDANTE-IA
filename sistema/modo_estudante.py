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
        self._conteudos = []
        self._pdfs = []
        self._servico_resumo = ServicoResumo()
        self._servico_ocr = ServicoOCR()
        self._servico_ocr_api = (
            ServicoOCRSpace() if OCR_PROVEDOR == "ocrspace" else None
        )
        self._proximo_id = 1

        self._carregar_dados()

    def _carregar_dados(self):
        """Lê o JSON da última sessão e ajusta o próximo id. Se o arquivo estiver
        inválido, avisa e começa vazio.
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
        try:
            ServicoArmazenamento.salvar(self._conteudos, self._pdfs)

        except RuntimeError as erro:
            print(f"\n⚠️ {erro}")

    def exibir_menu(self):
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
        print("9 - Ver conteúdos do Modo Estudante")
        print("10 - Sobre o projeto")
        print("0 - Sair")

        return input("\nEscolha uma opção: ").strip()

    @staticmethod
    def _perguntar_sim_nao(pergunta):
        while True:
            resposta = input(f"\n{pergunta} (sim/não): ").lower().strip()

            if resposta in ("sim", "s"):
                return True

            if resposta in ("não", "nao", "n"):
                return False

            print("\n⚠️ Resposta inválida. Digite sim ou não.")

    def _novo_conteudo(self, texto):
        # Só cria o objeto; quem chamou é que coloca na lista
        conteudo = Conteudo(self._proximo_id, texto)

        self._proximo_id += 1

        return conteudo

    def _selecionar_conteudo(self):
        """Pede um id e devolve o conteúdo. Devolve None se a
        lista estiver vazia, o id não for número ou não existir.
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

    def _extrair_texto(self, caminho_imagem):
        """Lê o texto da imagem pela API OCR.space e, se ela falhar, usa o
        Tesseract local.
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
        try:
            resumo = self._servico_resumo.gerar_resumo(texto)

        except Exception as erro:
            print(f"\n⚠️ Não foi possível gerar o resumo: {erro}")
            resumo = ""

        conteudo.definir_resumo(resumo)

    def _aplicar_modo_estudante(self, conteudo, texto):
        """Se o texto parecer um documento ou material de estudo, ativa o Modo
        Estudante sozinho. Caso contrário, pergunta ao usuário.
        """
        if ServicoDocumento.detectar_documento(texto):
            print("\n📄 Possível documento detectado!")
            print("\n🚀 Modo Estudante ativado automaticamente!")
            conteudo.ativar_modo_estudante()
            return

        if self._perguntar_sim_nao("Ativar Modo Estudante?"):
            print("\n🚀 Modo Estudante ativado!")
            conteudo.ativar_modo_estudante()
        else:
            print("\nModo Estudante não foi ativado.")

    def _pdfs_do_conteudo(self, conteudo):
        return [pdf for pdf in self._pdfs if pdf.id_conteudo == conteudo.id]

    @staticmethod
    def _titulo_pdf(conteudo):
        # Usa a primeira linha do texto se ela for curta; senão, um título padrão
        for linha in conteudo.texto_principal.splitlines():
            linha = linha.strip()

            if linha:
                if len(linha) <= 60:
                    return linha
                break

        return f"{TITULO_PDF} - Conteúdo {conteudo.id}"

    def _exportar_pdf(self, conteudo):
        """Gera o PDF do conteúdo, registra o arquivo e salva os dados. Gerar de
        novo sobrescreve o arquivo sem duplicar o registro. Devolve o caminho
        do PDF.
        """
        origem = conteudo.imagem or conteudo.texto

        caminho = ServicoPDF.gerar_pdf(
            f"conteudo_{conteudo.id}.pdf",
            self._titulo_pdf(conteudo),
            conteudo.texto_principal,
            conteudo.resumo
        )

        if not any(pdf.nome == caminho for pdf in self._pdfs):
            self._pdfs.append(PDF(caminho, origem, conteudo.id))

        self._salvar_dados()

        return caminho

    def capturar_conteudo(self):
        """Pede um texto ou o caminho de uma imagem. Imagem segue para o OCR;
        texto ganha resumo, Modo Estudante e é salvo.
        """
        entrada = input(
            "\nDigite o conteúdo ou caminho da imagem: "
        ).strip()

        if not ServicoCaptura.validar_conteudo(entrada):
            print("\n⚠️ Conteúdo inválido!")
            return

        caminho = ServicoCaptura.limpar_caminho(entrada)

        if ServicoCaptura.eh_imagem(caminho):
            self._processar_caminho(caminho)
            return

        conteudo = self._novo_conteudo(entrada)

        self._gerar_resumo(conteudo, entrada)
        self._aplicar_modo_estudante(conteudo, entrada)

        self._conteudos.append(conteudo)
        self._salvar_dados()

        print("\n✅ Conteúdo salvo com sucesso!")
        print(f"ID: {conteudo.id}")
        print(f"Resumo: {conteudo.resumo}")

    def solicitar_imagem(self):
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
        if not os.path.exists(caminho):
            print("\n⚠️ A imagem não foi encontrada.")
            return

        self.processar_imagem(caminho)

    def processar_imagem(self, caminho_imagem):
        """Fluxo completo da imagem: melhora com OpenCV, extrai o texto por OCR,
        gera o resumo, aplica o Modo Estudante, salva e oferece o PDF. Erros de
        arquivo, OCR ou gravação aparecem na tela sem derrubar o programa.
        """
        print("\n🖼️ Processando imagem...")

        nome_sem_extensao = os.path.splitext(
            os.path.basename(caminho_imagem)
        )[0]

        caminho_melhorado = PASTA_IMAGENS / f"{nome_sem_extensao}_melhorada.png"

        try:
            ServicoImagem.melhorar_imagem(caminho_imagem, caminho_melhorado)

            print("✅ Imagem melhorada com OpenCV.")

            texto_extraido = self._extrair_texto(caminho_melhorado)

            if not texto_extraido:
                print("\n⚠️ Nenhum texto foi identificado na imagem.")
                return

            print("\n===== TEXTO EXTRAÍDO =====")
            print(texto_extraido)

            conteudo = self._novo_conteudo(caminho_imagem)
            conteudo.definir_imagem(caminho_imagem)
            conteudo.definir_texto_extraido(texto_extraido)

            self._gerar_resumo(conteudo, texto_extraido)
            self._aplicar_modo_estudante(conteudo, texto_extraido)

            self._conteudos.append(conteudo)
            self._salvar_dados()

            print("\n✅ Imagem processada e conteúdo salvo!")
            print(f"ID: {conteudo.id}")

            if self._perguntar_sim_nao("Deseja gerar um PDF?"):
                caminho_pdf = self._exportar_pdf(conteudo)

                print(f"\n📄 PDF gerado: {caminho_pdf}")

        except (FileNotFoundError, ValueError, RuntimeError, OSError) as erro:
            print(f"\n❌ Erro durante o processamento: {erro}")

    def visualizar_conteudos(self):
        if not self._conteudos:
            print("\n⚠️ Nenhum conteúdo salvo.")
            return

        print("\n===== CONTEÚDOS CAPTURADOS =====")

        total = len(self._conteudos)

        for posicao, conteudo in enumerate(self._conteudos, start=1):
            print(f"\n--- Conteúdo {posicao} de {total} ---", end="")
            conteudo.exibir()

    def buscar_conteudo(self):
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
        """Troca o texto do conteúdo e refaz o resumo."""
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
        conteudo = self._selecionar_conteudo()

        if conteudo is None:
            return

        if not self._perguntar_sim_nao("Tem certeza que deseja remover?"):
            print("\nOperação cancelada.")
            return

        # Apaga também os PDFs gerados a partir desse conteúdo
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
        conteudo = self._selecionar_conteudo()

        if conteudo is None:
            return

        try:
            caminho = self._exportar_pdf(conteudo)

        except (OSError, ValueError, RuntimeError) as erro:
            print(f"\n❌ Erro ao gerar o PDF: {erro}")
            return

        print("\n✅ PDF gerado com sucesso!")
        print(f"📄 Arquivo: {caminho}")

    def visualizar_pdfs(self):
        if not self._pdfs:
            print("\n⚠️ Nenhum PDF gerado.")
            return

        print("\n===== PDFs GERADOS =====")

        for indice, pdf in enumerate(self._pdfs, start=1):
            print(f"\n{indice} - ")
            pdf.exibir()

    def visualizar_modo_estudante(self):
        ativos = [
            conteudo for conteudo in self._conteudos if conteudo.modo_estudante
        ]

        if not ativos:
            print("\n⚠️ Nenhum conteúdo no Modo Estudante.")
            return

        print(f"\n===== MODO ESTUDANTE ({len(ativos)}) =====")

        for conteudo in ativos:
            conteudo.exibir()

    def sobre_projeto(self):
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
            "Quando o conteúdo parece material de estudo, o Modo Estudante "
            "ativa sozinho e o conteúdo fica separado na opção 9."
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
        """Loop principal: mostra o menu, chama a ação escolhida e volta ao
        menu.
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
            "9": self.visualizar_modo_estudante,
            "10": self.sobre_projeto,
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
            print("\n\n👋 Encerrando o programa...")
