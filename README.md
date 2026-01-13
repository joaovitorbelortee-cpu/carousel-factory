# Carousel Factory v5.0

Fabrica de Carrosseis Virais com IA - Gere carrosseis profissionais para Instagram/TikTok automaticamente.

## Features

- **5 Formatos Mestres** baseados no modelocarrosel.md (Dark Stoic Bible)
- **Geracao Automatica de Copy** - apenas escolha o nicho
- **Temas Pre-Cadastrados** por nicho (Fitness, Financas, Produtividade, etc)
- **Galeria com Preview** de todos os slides
- **Download em ZIP** com um clique

## Nichos Disponiveis

- 💪 Fitness
- ⚡ Produtividade  
- 💰 Financas
- ❤️ Relacionamentos
- 🚀 Empreendedorismo
- 🧠 Mentalidade

## Instalacao

```bash
git clone https://github.com/SEU_USUARIO/carousel-factory.git
cd carousel-factory
pip install -r requirements.txt
python web_panel.py
```

## Como Usar

1. Acesse `http://localhost:5000`
2. Selecione um nicho
3. (Opcional) Digite um tema personalizado
4. Clique em "Gerar Carrossel com IA"
5. Baixe os slides na Galeria

## Tecnologias

- Python 3.10+
- Flask
- Pillow (PIL)
- Google Gemini API (opcional)

## Formatos de Carrossel

1. **O Dicionario** - Redefinicao de palavras
2. **O Diagnostico** - Checklists/Sinais
3. **O Conflito** - Comparacoes (VS)
4. **O Lembrete** - Frases de impacto
5. **O Algoritmo** - Passos/Fases

## Estrutura

```
carousel-factory/
├── web_panel.py          # Servidor Flask
├── gemini_integration.py # Geracao de copy
├── carousel_generator.py # Geracao de imagens
├── modelocarrosel.md     # Templates de referencia
├── logger.py             # Sistema de logs
├── requirements.txt      # Dependencias
└── output/carousels/     # Carrosseis gerados
```

## License

MIT License