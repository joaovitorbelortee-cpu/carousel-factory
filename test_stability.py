import subprocess
import sys
import time

def run_test(iteration):
    print(f"\n🔬 Teste de Estabilidade {iteration}/5")
    try:
        # Executar main.py no modo teste
        result = subprocess.run(
            [sys.executable, "main.py", "--test"], 
            capture_output=True, 
            text=True, 
            check=True
        )
        print("✅ Sucesso!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Falha no teste {iteration}")
        print(f"Erro: {e.stderr}")
        return False

def main():
    print("🚀 Iniciando verificação de estabilidade (5 execuções)...")
    
    failures = 0
    for i in range(1, 6):
        if not run_test(i):
            failures += 1
        time.sleep(1)  # Pequena pausa entre testes
    
    print("\n" + "="*40)
    print("📊 RELATÓRIO DE ESTABILIDADE")
    print("="*40)
    
    if failures == 0:
        print("🎉 TODOS OS TESTES PASSARAM! (5/5)")
        print("✅ O sistema está estável e pronto para produção.")
        sys.exit(0)
    else:
        print(f"⚠️ Houve {failures} falhas em 5 testes.")
        sys.exit(1)

if __name__ == "__main__":
    main()

