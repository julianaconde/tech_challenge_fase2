"""
Template Flask para interface web com Gemini via llm_integration.py
Necessário: pip install flask requests
"""
from flask import Flask, render_template_string, request
from llm_integration import (
    gerar_instrucoes_rota,
    gerar_relatorio,
    sugerir_melhorias,
    responder_pergunta,
)

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="pt-br">
<head>
    <meta charset="UTF-8">
    <title>LLM Gemini – Rotas & Entregas</title>
</head>
<body>
    <h2>LLM Gemini – Rotas & Entregas</h2>
    <form method="post">
        <label>Tipo de consulta:</label>
        <select name="tipo">
            <option value="instrucoes">Instruções para Motoristas</option>
            <option value="relatorio">Relatório de Eficiência</option>
            <option value="melhorias">Sugestão de Melhorias</option>
            <option value="pergunta">Pergunta sobre Rotas/Entregas</option>
        </select><br><br>
        <label>Dados/Texto:</label><br>
        <textarea name="dados" rows="6" cols="60"></textarea><br><br>
        <label>Pergunta (se aplicável):</label><br>
        <input type="text" name="pergunta" size="60"><br><br>
        <button type="submit">Enviar</button>
    </form>
    {% if resposta %}
    <h3>Resposta:</h3>
    <pre>{{ resposta }}</pre>
    {% endif %}
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
        
        # Chave Gemini diretamente no código (temporário para teste)
        api_key = "AIzaSyAxiTsdSN8mJrBtpCVb-DWuOjkTUxR6IZ8"
        
        if tipo == 'instrucoes':
            resposta = gerar_instrucoes_rota(dados, api_key)
        elif tipo == 'relatorio':
            resposta = gerar_relatorio(dados, api_key)
        elif tipo == 'melhorias':
            resposta = sugerir_melhorias(dados, api_key)
        elif tipo == 'pergunta':
            resposta = responder_pergunta(pergunta, dados, api_key)
    return render_template_string(HTML, resposta=resposta)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
