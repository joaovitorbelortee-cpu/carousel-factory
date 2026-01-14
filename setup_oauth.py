import os
import subprocess

def run_vercel_env(key, value):
    print(f"Configurando {key} no Vercel (Production)...")
    # Comando: echo value | vercel env add KEY production
    # Precisamos tratar o pipe
    cmd = f'echo {value} | vercel env add {key} production'
    # No Windows PowerShell/CMD o pipe funciona assim tambem via shell=True
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ {key} configurado!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro ao configurar {key}: {e}")

def main():
    print("="*60)
    print(" CONFIGURADOR OAUTH AUTOMATICO (Vercel)")
    print("="*60)
    print("Este script vai configurar suas chaves do Google no Vercel para voce.")
    print("Pegue as chaves em: https://console.cloud.google.com/apis/credentials\n")

    client_id = input("Cole o CLIENT ID aqui: ").strip()
    if not client_id:
        print("Cancelado.")
        return

    client_secret = input("Cole o CLIENT SECRET aqui: ").strip()
    if not client_secret:
        print("Cancelado.")
        return

    print("\nIniciando configuracao (pode pedir confirmacao do Vercel)...")
    
    # 1. Configurar Client ID
    run_vercel_env("GOOGLE_CLIENT_ID", client_id)
    
    # 2. Configurar Secret
    run_vercel_env("GOOGLE_CLIENT_SECRET", client_secret)
    
    # 3. Configurar Redirect URI
    redirect_uri = "https://viral-bot-two.vercel.app/oauth2callback"
    run_vercel_env("REDIRECT_URI", redirect_uri)
    
    # 4. Secret do Flask (Aleatorio)
    import secrets
    run_vercel_env("SECRET_KEY", secrets.token_hex(16))

    print("\n" + "="*60)
    print("✅ TUDO PRONTO! AGORA O LOGIN VAI FUNCIONAR.")
    print("Visite: https://viral-bot-two.vercel.app")
    print("="*60)

if __name__ == "__main__":
    main()
