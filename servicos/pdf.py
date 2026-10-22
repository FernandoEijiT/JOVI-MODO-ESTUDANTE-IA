from xml.sax.saxutils import escape
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
from configuracao import PASTA_PDFS

class ServicoPDF:

    """Gera os arquivos PDF, com título, resumo e conteúdo original."""
    @staticmethod
    def _paragrafos(texto, estilo):

        """Quebra o texto em blocos (separados por linha em branco) e transforma
        cada um em um parágrafo do ReportLab, usando o estilo recebido. Devolve
        a lista de parágrafos.
        """
        blocos = [
            bloco.strip()
            for bloco in texto.replace("\r", "").split("\n\n")
            if bloco.strip()
        ]

        return [
            # escape() evita que caracteres como <, > e & sejam
            # interpretados como marcação pelo ReportLab
            Paragraph(escape(bloco).replace("\n", "<br/>"), estilo)
            for bloco in blocos
        ]

    @staticmethod
    def gerar_pdf(
        nome_arquivo,
        titulo,
        texto,
        resumo
    ):

        """Cria o PDF na pasta de PDFs com o título, o resumo (se não estiver
        vazio) e o conteúdo original.

        Recebe o nome do arquivo (como "conteudo_1.pdf"), o título, o texto e o
        resumo. Devolve o caminho do arquivo criado.
        """
        PASTA_PDFS.mkdir(parents=True, exist_ok=True)

        caminho = PASTA_PDFS / nome_arquivo

        estilos = getSampleStyleSheet()

        estilo_titulo = estilos["Title"]
        estilo_secao = estilos["Heading2"]

        estilo_corpo = ParagraphStyle(
            "Corpo",
            parent=estilos["BodyText"],
            fontSize=11,
            leading=16,
            alignment=TA_JUSTIFY,
            spaceAfter=8
        )

        documento = SimpleDocTemplate(
            str(caminho),
            pagesize=A4,
            leftMargin=2 * cm,
            rightMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
            title=titulo
        )

        elementos = [
            Paragraph(escape(titulo), estilo_titulo),
            Spacer(1, 12)
        ]

        if resumo and resumo.strip():

            elementos.append(Paragraph("Resumo", estilo_secao))
            elementos.extend(
                ServicoPDF._paragrafos(resumo, estilo_corpo)
            )
            elementos.append(Spacer(1, 12))

        elementos.append(Paragraph("Conteúdo original", estilo_secao))
        elementos.extend(
            ServicoPDF._paragrafos(texto, estilo_corpo)
        )

        documento.build(elementos)

        return str(caminho)
