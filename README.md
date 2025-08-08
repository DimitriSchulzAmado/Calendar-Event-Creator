# Calendar Event Creator

Projeto Python para criação de eventos no Google Calendar a partir de um gatilho vindo do Notion.

## 📚 Bibliotecas Utilizadas

- google-auth, google-auth-oauthlib, google-auth-httplib2, google-api-python-client
- python-dotenv
- requests

## 🛠️ Padrões de Projeto

- Organização em módulos
- Uso de variáveis de ambiente (.env) para credenciais sensíveis

## ⚙️ Setup e Configuração

1. Clone o repositório:
   ```
   git clone https://github.com/DimitriSchulzAmado/Calendar-Event-Creator.git
   cd Calendar-Event-Creator
   ```
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```
3. Crie um arquivo `.env` na raiz do projeto com as variáveis:

   ```
   GOOGLE_CALENDAR_CREDENTIALS='{"type":"...","project_id":"...",...}'
   GOOGLE_TOKEN='{"token": "...", ...}'
   ```

   > Dica: Use JSON minificado (tudo em uma linha, aspas simples externas).

4. Execute o projeto conforme sua necessidade (exemplo):
   ```
   python main.py
   ```

## 🔍 Observações

- Não envie arquivos de credenciais para o repositório.
- Para uso no Heroku, defina as variáveis de ambiente pelo painel da plataforma.

<div class="footer" style="text-align: center; margin-top: 20px; color: #00FFFF">
    🚀 Desenvolvido e mantido por Dimitri Schulz Amado
</div>
