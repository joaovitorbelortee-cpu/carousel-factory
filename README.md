# Carousel Factory v6.0 - Business Edition

Fabrica de Carrosseis Virais com IA + Autenticacao Firebase.

## Features

- **Auth Via Firebase:** Login seguro com email/senha.
- **IA Gemini Pro:** Geracao de roteiros baseados no "Black Stoic Bible".
- **Visual Premium:** Interface estilo Bento Grid com Modo Caverna.
- **Download ZIP:** Baixe todos os slides prontos.

## Instalação

1. Clone o repositorio:
   ```bash
   git clone https://github.com/jonabergamo/carousel-factory.git
   cd carousel-factory
   ```

2. Instale dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure o `.env`:
   - Copie `.env.example` para `.env`
   - Cole sua `GEMINI_API_KEY`
   - (Opcional) Cole `FIREBASE_API_KEY` e `FIREBASE_PROJECT_ID` para ativar login.

4. Configuração Firebase (Para Auth):
   - Crie um projeto no console.firebase.google.com
   - Ative "Authentication" > "Email/Password"
   - Crie um usuário no console.
   - Em "Project Settings", pegue o `Project ID` e `Web API Key`.
   - Coloque no `.env`.
   - (Para Backend Seguro) Gere uma nova chave privada em "Service Accounts", baixe o JSON, renomeie para `firebase-adminsdk.json` e coloque na raiz do projeto.

5. Rodar:
   ```bash
   python web_panel.py
   ```
   Acesse: `http://localhost:5000`

## Tecnologias

- Flask
- Firebase Auth (Frontend + Admin SDK)
- Google Gemini API
- Pillow (Processamento de Imagem)

## License

MIT