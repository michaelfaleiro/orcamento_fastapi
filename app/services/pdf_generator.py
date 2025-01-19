from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from io import BytesIO

def gerar_pdf(orcamento):
    """
    Gera o PDF do orçamento com cabeçalho, tabela de produtos e valor final.
    
    :param orcamento: Dicionário com informações do orçamento
    :return: Conteúdo binário do PDF
    """
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)

    # Espaçamento
    espacamento = 20  # Espaçamento entre as linhas
    
    # Cabeçalho com informações da empresa e logo
    empresa_nome = "Oficina Garage345"
    empresa_endereco = "Av General Eurico Dutra 345, Estreito, Florianópolis/SC"
    empresa_contato = "Telefone: (48) 1234-5678"
    
    # Adiciona logo da empresa (substitua o caminho para o logo real)
    pdf.drawImage("logo.png", 455, 730, width=100, height=50)  # Altere o caminho da imagem conforme necessário
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, 770, empresa_nome)
    pdf.setFont("Helvetica", 10)
    pdf.drawString(50, 755, empresa_endereco)
    pdf.drawString(50, 740, empresa_contato)

    # Pular linha
    y = 710
    y -= espacamento

    # Informações do Orçamento
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(250, y, "Orçamento")
    y -= espacamento * 2  # Espaço maior após o título

    # Informações do Veículo e Placa
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, f"Veículo: {orcamento['veiculo'].upper()}")
    y -= espacamento
    pdf.drawString(50, y, f"Placa: {orcamento['placa'].upper()}")
    y -= espacamento * 2  # Espaço maior após as informações do veículo

    # Desenhando a Tabela de Produtos
    pdf.setFont("Helvetica-Bold", 10)

    # Cabeçalho da Tabela
    pdf.setStrokeColor(colors.black)
    pdf.setFillColor(colors.lightgrey)
    pdf.rect(50, y, 70, 20, fill=1)  # Cabeçalho "Quantidade"
    pdf.rect(120, y, 230, 20, fill=1)  # Cabeçalho "Descrição"
    pdf.rect(350, y, 100, 20, fill=1)  # Cabeçalho "Valor Unitário"
    pdf.rect(450, y, 100, 20, fill=1)  # Cabeçalho "Total"
    pdf.setFillColor(colors.black)
    pdf.drawString(55, y + 5, "Quantidade")
    pdf.drawString(125, y + 5, "Descrição")
    pdf.drawString(370, y + 5, "Valor Unitário")
    pdf.drawString(490, y + 5, "Total")
    y -= 20  # Espaço após o cabeçalho da tabela

    # Desenhando as linhas da tabela com os itens
    total_geral = 0
    
    for produto in orcamento["produtos"]:
        total_produto = produto["quantidade"] * produto["preco_unitario"]
        total_geral += total_produto
        
        # Linha do Produto
        pdf.setFont("Helvetica", 10)
        
        # Desenhando as células da linha
        pdf.rect(50, y, 70, 20)  # Quantidade
        pdf.rect(120, y, 230, 20)  # Descrição
        pdf.rect(350, y, 100, 20)  # Valor Unitário
        pdf.rect(450, y, 100, 20)  # Total
        
        # Preenchendo as células com o conteúdo
        pdf.drawString(55, y + 5, str(produto["quantidade"]))
        pdf.drawString(125, y + 5, produto["nome"].upper())
        pdf.drawString(403, y + 5, f"R${produto['preco_unitario']:.2f}")
        pdf.drawString(503, y + 5, f"R${total_produto:.2f}")
        
        # Linha de separação entre os produtos
        y -= 20  # Pula uma linha para o próximo produto
        

    # Linha de fechamento da tabela com o total
    y -= 20  # Espaço após a última linha do produto
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(455, y, f"Total: R${total_geral:.2f}")

    # Linha observações
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(50, y - 30, "Observações: Orçamento preliminar após a desmontagem do veículo podem haver alterações.")

    # Finalizando o PDF
    pdf.save()

    # Retorna o conteúdo do PDF gerado
    buffer.seek(0)
    return buffer.getvalue()
