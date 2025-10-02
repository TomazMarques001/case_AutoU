# Classificador de Emails (AutoU)

Este repositório contém uma aplicação Flask simples que envia o conteúdo de um email (texto ou PDF) para uma API de IA (OpenAI ou Gemini) e retorna uma classificação de produtividade (0-5) e uma categoria.

Passos rápidos:

1. Configure um repositório no GitHub e faça push deste diretório.


## Como rodar localmente

1. Instale o Python 3.10+ em seu computador.
2. Instale as dependências:
   ```powershell
   pip install -r requirements.txt
   ```
3. Execute o servidor Flask:
   ```powershell
   python app.py
   ```
4. Acesse a aplicação em [http://localhost:5000](http://localhost:5000) pelo navegador.

5. Adicione sua chave da API no campo do front-end para testar a classificação.

Notas:
- Não compartilhe sua chave de API publicamente.
- O `requirements.txt` inclui pacotes para sumarização local; remova se não for usar.
