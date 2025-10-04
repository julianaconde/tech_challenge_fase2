"""
Módulo de integração com Google Gemini (via API REST).
Necessário: chave de API Gemini, requests instalado (pip install requests).
"""
import requests
import os

def gemini_chat(prompt, api_key=None, model="gemini-2.5-flash"):
    """
    Envia um prompt para o Gemini e retorna a resposta.
    Usando modelo gemini-2.5-flash estável com v1beta
    """
    if api_key is None:
        api_key = os.getenv("GEMINI_API_KEY")
    
    # Verificar se a chave foi encontrada
    if not api_key:
        return "ERRO: Chave de API Gemini não encontrada. Exporte GEMINI_API_KEY antes de executar."
    
    # Endpoint com modelo gemini-2.5-flash disponível
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        resp = requests.post(url, json=data, headers=headers)
        resp.raise_for_status()
        return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
    except requests.exceptions.HTTPError as e:
        return f"ERRO HTTP: {e}\nURL: {url}\nResponse: {resp.text if 'resp' in locals() else 'N/A'}"
    except Exception as e:
        return f"ERRO: {str(e)}"

# Exemplos de prompts para cada caso:
PROMPT_INSTRUCOES = """
Gere instruções detalhadas para motoristas e equipes de entrega com base na seguinte rota otimizada:
{rota}
Considere pontos de parada, horários, restrições e recomendações de segurança.
"""

PROMPT_RELATORIO = """
Crie um relatório semanal sobre eficiência das rotas, economia de tempo e recursos, usando os dados abaixo:
{dados}
Estruture o relatório em tópicos e destaque oportunidades de melhoria.
"""

PROMPT_MELHORIAS = """
Analise os padrões das rotas e entregas abaixo e sugira melhorias para aumentar eficiência, reduzir custos e otimizar recursos:
{historico}
"""

PROMPT_PERGUNTA = """
Responda em linguagem natural à seguinte pergunta sobre rotas e entregas, usando os dados disponíveis:
Pergunta: {pergunta}
Dados: {contexto}
"""

# Funções utilitárias para cada caso

def gerar_instrucoes_rota(rota, api_key=None):
    prompt = PROMPT_INSTRUCOES.format(rota=rota)
    return gemini_chat(prompt, api_key)

def gerar_relatorio(dados, api_key=None):
    prompt = PROMPT_RELATORIO.format(dados=dados)
    return gemini_chat(prompt, api_key)

def sugerir_melhorias(historico, api_key=None):
    prompt = PROMPT_MELHORIAS.format(historico=historico)
    return gemini_chat(prompt, api_key)

def responder_pergunta(pergunta, contexto, api_key=None):
    prompt = PROMPT_PERGUNTA.format(pergunta=pergunta, contexto=contexto)
    return gemini_chat(prompt, api_key)
