# Diretiva: Pesquisar Tendências

## Objetivo
Identificar tópicos, hooks e hashtags em alta para um nicho específico.

## Inputs
- `nicho` (string): Tema a pesquisar (ex: "Ferramentas de IA")
- `force_refresh` (bool): Ignorar cache e buscar novamente

## Ferramentas (execution/)
1. `trend_researcher.py` - Script principal de pesquisa

## Fluxo
1. Verificar cache em `.tmp/cache/trends_{nicho}.json`
2. Se cache válido (<6h), usar dados cacheados
3. Se cache inválido ou `force_refresh=True`:
   - Buscar dados de `real_trends.json` (dados injetados)
   - Ou gerar dados simulados baseados em hooks virais conhecidos
4. Analisar padrões (duração média, engajamento, hashtags)
5. Retornar relatório de tendências

## Edge Cases
- Nicho desconhecido: usar hashtags genéricas ["Viral", "Trending", "Foryou"]
- Erro de rede: usar dados simulados

## Outputs
- Relatório JSON com:
  - `top_hashtags`: Lista de hashtags populares
  - `popular_hooks`: Frases de abertura que viralizam
  - `avg_duration`: Duração média recomendada
  - `recommended_styles`: Formatos sugeridos (listicle, pov, etc)
