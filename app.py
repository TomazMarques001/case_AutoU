from flask import Flask, render_template, request
import os
import pdfplumber
import requests
import json
import re

app = Flask(__name__)

# Função para classificar produtividade (0 a 5) e categoria em uma única requisição

def ia_classify_produtividade_categoria_openai(text, api_key):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {api_key}"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{
            "role": "user",
            "content": (
                "Analise o texto abaixo e responda em formato JSON com duas chaves: 'produtividade' (número de 0 a 5, onde 0 é improdutivo e 5 é muito produtivo) e 'categoria' (uma das opções: RH, Financeiro, Operacional, Parcerias, Burocrático).\n"
                "Apenas retorne o JSON.\n\nTexto:\n" + text
            )
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    if "choices" in resp_json:
        return resp_json["choices"][0]["message"]["content"]
    else:
        return f"Erro na resposta da API: {resp_json}"

def ia_classify_produtividade_categoria_gemini(text, api_key):
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
    headers = {"Content-Type": "application/json", "X-goog-api-key": api_key}
    prompt = (
        "Analise o texto abaixo e responda apenas com um JSON puro, sem explicações, sem marcação de bloco de código, contendo duas chaves: 'produtividade' (uma das: \"Totalmente improdutivo\",\"Muito improdutivo\",\"Baixa prioridade\",\"Média importância\",\"Importante\",\"Alta prioridade\") e 'categoria' (uma das opções: RH, Financeiro, Operacional, Parcerias, Burocrático).\n"
        "\n\nTexto:\n" + text
    )
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(url, headers=headers, json=data)
    resp_json = response.json()
    try:
        return resp_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return f"Erro na resposta da API:\n{json.dumps(resp_json, indent=2, ensure_ascii=False)}"
def extrair_json(texto):
    match = re.search(r"\{.*\}", texto, re.DOTALL)
    if match:
        return match.group(0)
    return "{}"

def extract_text_from_request(req):
    """Retorna o texto enviado no formulário ou extraído do arquivo (.txt/.pdf)."""
    text = req.form.get("emailText") or ""
    file = req.files.get("emailFile")
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext == ".txt":
            try:
                text = file.read().decode("utf-8")
            except Exception:
                # fallback: keep existing text if decode falhar
                pass
        elif ext == ".pdf":
            try:
                with pdfplumber.open(file) as pdf:
                    text = " ".join(page.extract_text() or '' for page in pdf.pages)
            except Exception:
                pass
    return text.strip() or None

@app.route("/", methods=["GET", "POST"])
def index():
    produtividade = None
    categoria = None
    texto_email = None
    erro_api = None
    if request.method == "POST":
        api_key = request.form.get("apiKey")
        ia_type = request.form.get("iaType")
        texto_email = extract_text_from_request(request)

        # Validações simples e mensagens claras
        if not api_key:
            erro_api = "Chave da API não fornecida."
        elif not texto_email:
            erro_api = "Nenhum texto ou arquivo válido enviado."
        elif not ia_type:
            erro_api = "Tipo de IA não selecionado."
        else:
            if ia_type == "openai":
                resultado = ia_classify_produtividade_categoria_openai(texto_email, api_key)
            elif ia_type == "gemini":
                resultado = ia_classify_produtividade_categoria_gemini(texto_email, api_key)
            else:
                resultado = "Tipo de IA não suportado."

            try:
                dados_str = extrair_json(resultado)
                dados = json.loads(dados_str)
                produtividade = dados.get("produtividade")
                categoria = dados.get("categoria")
                if produtividade is None and categoria is None:
                    erro_api = resultado
                else:
                    erro_api = None
            except Exception as e:
                erro_api = f"Falha no json.loads: {str(e)}\nResposta bruta:\n{dados_str if 'dados_str' in locals() else resultado}"

    return render_template("index.html", produtividade=produtividade, categoria=categoria, texto_email=texto_email, erro_api=erro_api)

if __name__ == "__main__":
    app.run(debug=True)