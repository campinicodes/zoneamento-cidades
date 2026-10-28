# Plataforma multicidades – consulta de zoneamento por polígono

App Flask que lê **qualquer** `cidades/<slug>/<slug>.json` no padrão `../PADRAO_JSON.md` (schema 1.1 – estrutura definida por `../schema/cidade.schema.json`; parâmetros lidos pela `forma`).
O motor (`motor.py`) é genérico: a zona aplicável sai só de `zonas[].tipo/prioridade/regra_sobreposicao`
e de `camadas_complementares[].papel`. Nenhuma regra é escrita para uma cidade específica.

> Resultado **indicativo**. Prevalecem o texto legal e a manifestação da prefeitura (`orgao_confirmacao` do JSON).

## Rodar
```bash
cd plataforma/app
pip install -r requirements.txt          # flask, shapely>=2, pyproj, numpy
python app.py                            # http://127.0.0.1:5000
# opcional: outras pastas de cidades (separadas por ':') e porta
PLATAFORMA_CIDADES="../cidades:../testes/cidades" PORT=5077 python app.py
```
Testes: `python3 ../testes/test_plataforma.py` (também roda com pytest).
Validador: `python3 ../validar_cidade.py <slug>` ou `--todas`, ou `--arquivo caminho.json`.

## O que a tela faz
- **Seletor de cidade**: lista as cidades descobertas e centraliza em `centro_mapa`. Com "Detectar automaticamente",
  a cidade de cada polígono é a que contém o centróide nas suas zonas base (aceita até 2 km fora, com bbox).
- **Desenhar** um ou vários polígonos/retângulos, ou **enviar KML/KMZ/GeoJSON**: todos os polígonos
  (cada Placemark) são analisados e têm um resultado próprio, cada um com sua cidade.
- Resultado por polígono: área (em `geografico.crs_area`, ou na UTM SIRGAS 2000 calculada pelo `centro_mapa`),
  zona aplicável e critério, zona dos índices, % por zona base/sobreposta, distância aos eixos,
  parâmetros com citação (`fonte_id`, lei, artigo e link), camadas complementares e alertas
  (restrições, divisas, eixos/testada, sobreposições parciais e "confirmar na prefeitura").
- **⬇ baixar resultado (JSON)** salva a resposta completa.
- **/referencias/<slug>** mostra as lacunas do JSON, os avisos do validador e o `REFERENCIAS.md` da cidade.
- Atalhos de URL: `/?cidade=<slug>&zonas=1&poligono=<GeoJSON url-encoded>`.

## API
| Rota | Uso |
|---|---|
| `GET /api/cidades` | cidades válidas (meta, bbox, se já foi carregada) e pastas inválidas com os erros |
| `GET /api/zonas/<slug>[?tipo=base]` | GeoJSON das zonas, para desenhar no mapa |
| `POST /api/consulta` | corpo `{"geojson": <Geometry/Feature/FeatureCollection>, "cidade": "<slug>"/null}` |
| `POST /api/consulta-arquivo` (alias `/api/consulta-kmz`) | multipart `arquivo` (.kml/.kmz/.geojson) e `cidade` opcional |
| `GET /referencias/<slug>` | página de referências e lacunas |
| `GET /api/validar/<slug>` | relatório completo do validador |

Resposta: `{"n_poligonos", "resultados": [{nome, geometria, cidade, terreno, resultado, parametros, parametros_zona_base, permeabilidade, macrozona, sobreposicoes, camadas_complementares, alertas, referencias}]}`.

## Motor genérico (resumo)
1. Zonas `base`: área e % de cada uma; a base predominante é a de maior área.
2. Candidatas a substituir a base: `sobreposta` com `efeito: substitui` e % ≥ `limiar_pct` (padrão 50), desde que
   `aplica_sobre` seja nulo ou inclua a base. Também `eixo` a ≤ `distancia_max_m` (padrão 50).
   Vence a maior `prioridade`; as outras candidatas viram alerta.
3. `usa_indices_de`: troca os índices da base (respeita `aplica_sobre` e `limiar_pct`); os itens em `mantem_da_base` ficam com o valor da base.
4. `apenas_alerta`: só alerta. `requer_testada`: alerta e devolve também `parametros_zona_base`.
5. Camadas: `permeabilidade` sobrescreve o parâmetro de mesmo nome com o código predominante. `macrozona` traz os parâmetros do código predominante.
   `restricao` gera um alerta por código que intersecta ou fica a ≤ `raio_divisa_m`. `informativa` só é listada.
6. Lazy loading: na partida só o metadado e o bbox são lidos. Os índices STRtree (em metros) são montados na 1ª consulta de cada cidade.

## Arquivos
`app.py` (rotas, leitura KML/KMZ/GeoJSON, markdown→HTML) · `motor.py` (motor, cidade, registro) ·
`templates/` · `static/` · `screenshot.png` · `screenshot_referencias.png`.

## Página inicial, status e desempenho (27/10/2026)
- A página inicial lista as cidades cadastradas com nº de zonas, % da área base com geometria oficial, erro estimado, data de levantamento e nº de lacunas, mais o link para `/referencias/<slug>`. Os números saem de `motor.status_cidade()`, em `GET /api/cidades` → `status`.
- Descoberta em cache (`.cache_descoberta.json`, invalidado por mtime/tamanho do JSON, do schema, do validador e do motor). Carga lazy por cidade e STRtree métrica. Rio (18 MB): 1ª consulta ≈ 1,3 s, seguintes ≈ 20 ms.
- Screenshots: `screenshot_final.png` (consulta em Curitiba, zona ZFR, com zonas visíveis) e `screenshot_inicio.png` (tabela de status).
