from flask import Flask, request, jsonify
import google.genai as genai
from google.genai import types, errors
from dotenv import load_dotenv
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent
# Carrega o .env localizado em /motionfit/api/.env (conforme instruído)
load_dotenv(BASE_DIR / ".env")

app = Flask(__name__)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError(
        "A chave da API do Gemini não foi encontrada. "
        "Certifique-se de definir GEMINI_API_KEY no arquivo .env."
    )

# Cliente Google GenAI
client = genai.Client(api_key=api_key)

@app.route('/perguntas', methods=['POST'])
def perguntas():
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict) or "pergunta" not in dados:
        return jsonify({
            "erro": "Envie os dados no formato JSON com a chave 'pergunta'."
        }), 400

    pergunta = dados["pergunta"]

    if not isinstance(pergunta, str) or not pergunta.strip():
        return jsonify({
            "erro": "A pergunta deve ser uma string não vazia."
        }), 400

    system_prompt = (
        "Você é Artemis, um assistente virtual criado para ajudar "
        "com perguntas e fornecer informações úteis. "
        "Sempre responda em português do Brasil."
    )

    try:
        # Chamada ao Gemini
        resposta = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=pergunta,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                # valores padrão razoáveis; ajuste se necessário
                temperature=0.7,
                max_output_tokens=512,
            ),
        )

        # Priorizar texto simples retornado pela SDK
        texto = getattr(resposta, "text", None)
        if not texto:
            # Se não houver texto, tratar como erro do serviço
            app.logger.error("Resposta do Gemini sem campo 'text'", extra={"details": getattr(resposta, 'details', None)})
            return jsonify({"erro": "Resposta inesperada do serviço de IA."}), 502

        return jsonify({"resposta": texto}), 200

    except errors.ClientError as e:
        # Erros 4xx vindos da API
        status = (getattr(e, 'status', '') or '').lower() if hasattr(e, 'status') else ''
        message = (getattr(e, 'message', '') or '').lower() if hasattr(e, 'message') else str(e).lower()
        code = getattr(e, 'code', None)

        # Autenticação / chave inválida
        if code == 401 or 'api_key_invalid' in message or 'api key not valid' in message or 'invalid api key' in message:
            app.logger.error("Autenticação Gemini falhou (verificar GEMINI_API_KEY)", exc_info=True)
            return jsonify({"erro": "Erro de autenticação. Verifique a configuração da API."}), 401

        # Modelo não encontrado
        if code == 404 or 'not_found' in status or 'not found' in message:
            app.logger.error(f"Modelo não encontrado ou indisponível: {code} {status} {message}")
            return jsonify({"erro": "Modelo não disponível. Atualize para 'gemini-3.8-flash' ou verifique permissões."}), 404

        # Limite/quota
        if 'quota' in message or 'rate limit' in message or code == 429:
            app.logger.warning(f"Quota/Rate limit atingido: {code} {message}")
            return jsonify({"erro": "Limite de requisições atingido. Tente novamente mais tarde."}), 429

        # Outros 4xx
        app.logger.error(f"ClientError do Gemini: {code} {status} {message}", exc_info=True)
        return jsonify({"erro": "Erro na requisição para o serviço de IA."}), 400

    except errors.ServerError as e:
        # Erros 5xx vindos da API
        app.logger.error(f"Erro do serviço Gemini (server): {getattr(e,'code',None)} {getattr(e,'message',None)}", exc_info=True)
        return jsonify({"erro": "Serviço de IA indisponível. Tente novamente mais tarde."}), 502

    except Exception as e:
        # Erro genérico não previsto
        app.logger.exception(f"Erro inesperado ao consultar a API GEMINI: {e}")
        return jsonify({"erro": "Não foi possível processar a pergunta agora."}), 500


if __name__ == '__main__':
    app.run(debug=True)