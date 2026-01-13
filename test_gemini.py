import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key or "Cole_Sua" in api_key:
        print("\n❌ ERRO: GEMINI_API_KEY não encontrada no arquivo .env!")
        print("Vá em https://aistudio.google.com/ e gere sua chave gratuita.")
        return False
        
    print(f"🔄 Testando conexão com a API Key: {api_key[:10]}...")
    
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Responda apenas 'CONEXÃO OK'")
        
        if "CONEXÃO OK" in response.text.upper():
            print("✅ SUCESSO! O Gemini está ativo e respondendo.")
            return True
        else:
            print(f"⚠️ Resposta inesperada: {response.text}")
            return False
    except Exception as e:
        print(f"❌ ERRO NA API: {e}")
        return False

if __name__ == "__main__":
    test_connection()
