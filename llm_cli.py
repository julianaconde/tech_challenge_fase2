"""
Exemplo de interface CLI para integração com Gemini via llm_integration.py
Necessário: requests instalado, chave de API Gemini exportada como GEMINI_API_KEY
"""
import argparse
from llm_integration import (
    gerar_instrucoes_rota,
    gerar_relatorio,
    sugerir_melhorias,
    responder_pergunta,
)

parser = argparse.ArgumentParser(description="Interface CLI para LLM Gemini")
subparsers = parser.add_subparsers(dest="comando")

sp1 = subparsers.add_parser("instrucoes", help="Gerar instruções para motoristas")
sp1.add_argument("--rota", required=True, help="Dados da rota otimizada")

sp2 = subparsers.add_parser("relatorio", help="Gerar relatório de eficiência")
sp2.add_argument("--dados", required=True, help="Dados agregados das rotas")

sp3 = subparsers.add_parser("melhorias", help="Sugerir melhorias de processo")
sp3.add_argument("--historico", required=True, help="Histórico de rotas e entregas")

sp4 = subparsers.add_parser("pergunta", help="Perguntar sobre rotas/entregas")
sp4.add_argument("--pergunta", required=True, help="Pergunta em linguagem natural")
sp4.add_argument("--contexto", required=True, help="Contexto/dados das rotas")

args = parser.parse_args()

if args.comando == "instrucoes":
    print(gerar_instrucoes_rota(args.rota))
elif args.comando == "relatorio":
    print(gerar_relatorio(args.dados))
elif args.comando == "melhorias":
    print(sugerir_melhorias(args.historico))
elif args.comando == "pergunta":
    print(responder_pergunta(args.pergunta, args.contexto))
else:
    parser.print_help()
