"""
Template Flask para interface web com Gemini via llm_integration.py
Necessário: pip install flask requests
"""

from flask import Flask, render_template_string, request, make_response, session
from llm_integration import (
    gerar_instrucoes_rota,
    gerar_relatorio,
    sugerir_melhorias,
    responder_pergunta,
)
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

# Carregar variáveis do .env automaticamente
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)
app.secret_key = 'gemini_rotas_secret_key_2025'

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>LLM Gemini – Rotas & Entregas</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
            line-height: 1.6;
        }
        .container {
            background: white;
            padding: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 {
            color: #2c3e50;
            text-align: center;
            margin-bottom: 30px;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            font-weight: bold;
            color: #34495e;
            display: block;
            margin-bottom: 5px;
        }
        select, textarea, input[type="text"] {
            width: 100%;
            padding: 10px;
            border: 2px solid #bdc3c7;
            border-radius: 5px;
            font-size: 14px;
            transition: border-color 0.3s;
        }
        select:focus, textarea:focus, input[type="text"]:focus {
            border-color: #3498db;
            outline: none;
        }
        textarea {
            resize: vertical;
            min-height: 120px;
        }
        button {
            background: linear-gradient(135deg, #3498db, #2980b9);
            color: white;
            padding: 12px 30px;
            border: none;
            border-radius: 5px;
            cursor: pointer;
            font-size: 16px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        .btn-pdf {
            background: linear-gradient(135deg, #e74c3c, #c0392b);
            margin-left: 10px;
        }
        .btn-container {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        .resposta-container {
            margin-top: 30px;
            padding: 20px;
            background: #ecf0f1;
            border-radius: 8px;
            border-left: 5px solid #27ae60;
        }
        .resposta-titulo {
            color: #27ae60;
            margin-bottom: 15px;
            font-size: 1.2em;
        }
        .resposta-conteudo {
            background: white;
            padding: 20px;
            border-radius: 5px;
            border: 1px solid #bdc3c7;
            white-space: pre-wrap;
            font-family: 'Courier New', monospace;
            line-height: 1.5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚚 LLM Gemini – Rotas & Entregas</h1>
        <form method="post">
            <div class="form-group">
                <label for="tipo">Tipo de consulta:</label>
                <select name="tipo" id="tipo">
                    <option value="instrucoes">📋 Instruções para Motoristas</option>
                    <option value="relatorio">📊 Relatório de Eficiência</option>
                    <option value="melhorias">💡 Sugestão de Melhorias</option>
                    <option value="pergunta">❓ Pergunta sobre Rotas/Entregas</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="dados">Dados/Texto:</label>
                <textarea name="dados" id="dados" rows="6" placeholder="Cole aqui os dados das rotas otimizadas ou informações relevantes..."></textarea>
            </div>
            
            <div class="form-group">
                <label for="pergunta">Pergunta (se aplicável):</label>
                <input type="text" name="pergunta" id="pergunta" placeholder="Digite sua pergunta específica aqui...">
            </div>
            
            <div class="form-group">
                <div class="btn-container">
                    <button type="submit">🚀 Enviar Consulta</button>
                    {% if resposta %}
                    <a href="/exportar-pdf" target="_blank">
                        <button type="button" class="btn-pdf">📄 Exportar PDF</button>
                    </a>
                    {% endif %}
                </div>
            </div>
        </form>
        
        {% if resposta %}
        <div class="resposta-container">
            <h3 class="resposta-titulo">✅ Resposta do Gemini:</h3>
            <div class="resposta-conteudo">{{ resposta }}</div>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    resposta = None
    if request.method == 'POST':
        tipo = request.form['tipo']
        dados = request.form['dados']
        pergunta = request.form.get('pergunta', '')
        # Chave Gemini via variável de ambiente
        import os
        api_key = os.getenv("GEMINI_API_KEY")
        if tipo == 'instrucoes':
            resposta = gerar_instrucoes_rota(dados, api_key)
        elif tipo == 'relatorio':
            resposta = gerar_relatorio(dados, api_key)
        elif tipo == 'melhorias':
            resposta = sugerir_melhorias(dados, api_key)
        elif tipo == 'pergunta':
            resposta = responder_pergunta(pergunta, dados, api_key)
        
        # Salvar dados na sessão para o PDF
        session['ultima_resposta'] = resposta
        session['ultimo_tipo'] = tipo
        session['ultimos_dados'] = dados
        session['ultima_pergunta'] = pergunta
        
    return render_template_string(HTML, resposta=resposta)

@app.route('/exportar-pdf')
def exportar_pdf():
    """Gera e retorna um PDF com a última resposta gerada."""
    resposta = session.get('ultima_resposta', 'Nenhuma resposta disponível')
    tipo = session.get('ultimo_tipo', 'consulta')
    dados = session.get('ultimos_dados', '')
    pergunta = session.get('ultima_pergunta', '')
    
    # Criar PDF em memória
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1  # Centralizado
    )
    story.append(Paragraph("📊 Relatório de Rotas - Gemini AI", title_style))
    
    # Data e hora
    now = datetime.now().strftime("%d/%m/%Y às %H:%M")
    story.append(Paragraph(f"<b>Data:</b> {now}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Tipo de consulta
    tipo_map = {
        'instrucoes': '📋 Instruções para Motoristas',
        'relatorio': '📊 Relatório de Eficiência',
        'melhorias': '💡 Sugestão de Melhorias',
        'pergunta': '❓ Pergunta sobre Rotas/Entregas'
    }
    story.append(Paragraph(f"<b>Tipo de Consulta:</b> {tipo_map.get(tipo, tipo)}", styles['Normal']))
    story.append(Spacer(1, 12))
    
    # Dados de entrada (se houver)
    if dados:
        story.append(Paragraph("<b>Dados de Entrada:</b>", styles['Heading2']))
        # Quebrar texto longo em parágrafos
        dados_lines = dados.replace('\n', '<br/>')
        story.append(Paragraph(dados_lines, styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Pergunta (se houver)
    if pergunta:
        story.append(Paragraph(f"<b>Pergunta:</b> {pergunta}", styles['Normal']))
        story.append(Spacer(1, 12))
    
    # Resposta do Gemini
    story.append(Paragraph("<b>Resposta do Gemini AI:</b>", styles['Heading2']))
    # Quebrar resposta em parágrafos e preservar formatação
    resposta_lines = resposta.replace('\n', '<br/>')
    story.append(Paragraph(resposta_lines, styles['Normal']))
    
    # Rodapé
    story.append(Spacer(1, 30))
    story.append(Paragraph("Relatório gerado automaticamente pelo sistema de Rotas & Entregas com Gemini AI", styles['Italic']))
    
    # Construir PDF
    doc.build(story)
    
    # Preparar resposta
    buffer.seek(0)
    response = make_response(buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=relatorio_rotas_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
    
    return response

if __name__ == '__main__':
    app.run(debug=True, port=5002)
