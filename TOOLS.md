# MCP Brasil — Catálogo de Tools, Resources e Prompts

> Gerado em 2026-03-22. Total: **124 tools**, **30 resources**, **22 prompts** em **13 features**.

## Resumo por Feature

| Feature | Tools | Resources | Prompts | Auth |
|---------|------:|----------:|--------:|------|
| [BACEN](#bacen) | 8 | 3 | 2 | — |
| [BrasilAPI](#brasilapi) | 16 | 3 | 2 | — |
| [Câmara](#câmara) | 10 | 3 | 3 | — |
| [Compras (PNCP)](#compras) | 3 | 1 | 1 | — |
| [DataJud](#datajud) | 7 | 3 | 2 | `DATAJUD_API_KEY` |
| [Diário Oficial](#diário-oficial) | 3 | 1 | 1 | — |
| [IBGE](#ibge) | 9 | 3 | 2 | — |
| [Jurisprudência](#jurisprudência) | 6 | 3 | 2 | — |
| [Senado](#senado) | 22 | 3 | 3 | — |
| [TransfereGov](#transferegov) | 5 | 1 | 1 | — |
| [Transparência](#transparência) | 18 | 4 | 3 | `TRANSPARENCIA_API_KEY` |
| [TSE](#tse) | 8 | 2 | 2 | — |

---

## BACEN

Banco Central do Brasil — séries temporais, indicadores econômicos, câmbio.

### Tools (8)

| Tool | Descrição |
|------|-----------|
| `consultar_serie` | Consulta valores de uma série temporal do BCB por código |
| `ultimos_valores` | Obtém os últimos N valores de uma série temporal |
| `metadados_serie` | Obtém metadados/informações de uma série |
| `series_populares` | Lista as 190+ séries temporais disponíveis no catálogo |
| `buscar_serie` | Busca séries no catálogo por nome ou descrição |
| `indicadores_atuais` | Obtém os valores mais recentes dos principais indicadores (Selic, IPCA, etc.) |
| `calcular_variacao` | Calcula a variação percentual de uma série entre datas ou períodos |
| `comparar_series` | Compara 2 a 5 séries temporais no mesmo período |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `catalogo_series` | Catálogo completo das 193 séries temporais disponíveis |
| `categorias_series` | As 12 categorias de séries temporais com contagem |
| `indicadores_chave` | Os 5 indicadores principais: Selic, IPCA, IPCA 12m, Dólar PTAX, IBC-Br |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `analise_economica` | Panorama da conjuntura econômica brasileira |
| `comparar_indicadores` | Comparação de séries temporais específicas |

---

## BrasilAPI

Dados públicos consolidados — CEP, CNPJ, DDD, bancos, câmbio, FIPE, ISBN, NCM, PIX.

### Tools (16)

| Tool | Descrição |
|------|-----------|
| `consultar_cep` | Consulta endereço completo a partir de um CEP |
| `consultar_cnpj` | Consulta dados cadastrais de uma empresa pelo CNPJ |
| `consultar_ddd` | Consulta cidades e estado de um código DDD |
| `listar_bancos` | Lista todos os bancos brasileiros registrados no BCB |
| `consultar_banco` | Consulta dados de um banco específico pelo código |
| `listar_moedas` | Lista moedas disponíveis para consulta de câmbio |
| `consultar_cotacao` | Consulta cotação de uma moeda em relação ao Real em uma data |
| `consultar_feriados` | Lista todos os feriados nacionais de um ano |
| `consultar_taxa` | Consulta taxa ou índice oficial (Selic, CDI, IPCA) |
| `listar_tabelas_fipe` | Lista tabelas de referência FIPE |
| `listar_marcas_fipe` | Lista marcas de veículos FIPE por tipo |
| `buscar_veiculos_fipe` | Busca modelos de veículos FIPE por tipo e marca |
| `consultar_isbn` | Consulta dados de um livro pelo ISBN |
| `buscar_ncm` | Busca códigos NCM por descrição ou código |
| `consultar_pix_participantes` | Lista instituições participantes do PIX |
| `consultar_registro_br` | Consulta disponibilidade de domínio .br |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `taxas_disponiveis` | Catálogo de taxas e índices oficiais |
| `tipos_veiculo_fipe` | Tipos de veículo aceitos nas consultas FIPE |
| `endpoints_brasilapi` | Catálogo de todos os endpoints da BrasilAPI |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `analise_empresa` | Análise completa de uma empresa pelo CNPJ |
| `panorama_economico` | Panorama das principais taxas e indicadores |

---

## Câmara

Câmara dos Deputados — deputados, proposições, votações, despesas, comissões.

### Tools (10)

| Tool | Descrição |
|------|-----------|
| `listar_deputados` | Lista deputados federais em exercício com filtros opcionais |
| `buscar_deputado` | Busca detalhes de um deputado pelo ID |
| `buscar_proposicao` | Busca proposições legislativas (PL, PEC, MPV, etc.) |
| `consultar_tramitacao` | Consulta tramitação de uma proposição |
| `buscar_votacao` | Busca votações nominais em plenário ou comissões |
| `votos_nominais` | Consulta votos nominais de uma votação específica |
| `despesas_deputado` | Consulta despesas de cota parlamentar (CEAP) |
| `agenda_legislativa` | Consulta agenda da Câmara (sessões, audiências, reuniões) |
| `buscar_comissoes` | Busca comissões e órgãos legislativos |
| `frentes_parlamentares` | Lista frentes parlamentares |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `tipos_proposicao` | Tipos de proposição legislativa |
| `legislaturas_recentes` | Legislaturas recentes |
| `info_api` | Informações gerais sobre a API da Câmara |

### Prompts (3)

| Prompt | Descrição |
|--------|-----------|
| `acompanhar_proposicao` | Acompanhamento completo de uma proposição |
| `perfil_deputado` | Perfil completo de um deputado federal |
| `analise_votacao` | Análise detalhada de uma votação |

---

## Compras

PNCP (Portal Nacional de Contratações Públicas) — licitações, contratos, atas de preço.

### Tools (3)

| Tool | Descrição |
|------|-----------|
| `buscar_contratacoes` | Busca licitações e contratações públicas |
| `buscar_contratos` | Busca contratos públicos |
| `buscar_atas` | Busca atas de registro de preço |

### Resources (1)

| Resource | Descrição |
|----------|-----------|
| `modalidades_licitacao` | Modalidades de licitação conforme Lei 14.133/2021 |

### Prompts (1)

| Prompt | Descrição |
|--------|-----------|
| `investigar_fornecedor` | Investiga um fornecedor em contratações públicas |

---

## DataJud

CNJ (Conselho Nacional de Justiça) — processos judiciais via Elasticsearch.

### Tools (7)

| Tool | Descrição |
|------|-----------|
| `buscar_processos` | Busca processos judiciais por texto livre |
| `buscar_processo_por_numero` | Busca processo pelo número unificado (NPU) |
| `buscar_processos_por_classe` | Busca processos por classe processual |
| `buscar_processos_por_assunto` | Busca processos por assunto/tema |
| `buscar_processos_por_orgao` | Busca processos por órgão julgador |
| `buscar_processos_avancado` | Busca avançada com filtros por código e paginação |
| `consultar_movimentacoes` | Consulta movimentações de um processo |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `tribunais_disponiveis` | 91 tribunais disponíveis com siglas e nomes |
| `classes_processuais` | Classes processuais comuns |
| `info_api` | Informações gerais sobre a API DataJud |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `analise_processo` | Análise completa de um processo judicial |
| `pesquisa_juridica` | Pesquisa jurídica sobre um tema |

---

## Diário Oficial

Querido Diário — diários oficiais municipais.

### Tools (3)

| Tool | Descrição |
|------|-----------|
| `buscar_diarios` | Busca em diários oficiais municipais por texto livre |
| `buscar_cidades` | Busca municípios disponíveis pelo nome |
| `listar_territorios` | Lista todos os municípios com diários oficiais |

### Resources (1)

| Resource | Descrição |
|----------|-----------|
| `capitais_cobertas` | Capitais brasileiras com cobertura confirmada |

### Prompts (1)

| Prompt | Descrição |
|--------|-----------|
| `investigar_empresa` | Investiga menções de uma empresa em diários oficiais |

---

## IBGE

Instituto Brasileiro de Geografia e Estatística — localidades, nomes, agregados, CNAE, malhas.

### Tools (9)

| Tool | Descrição |
|------|-----------|
| `listar_estados` | Lista todos os 27 estados com sigla, nome e região |
| `buscar_municipios` | Busca municípios de um estado pela sigla da UF |
| `listar_regioes` | Lista as 5 macro-regiões do Brasil |
| `consultar_nome` | Consulta frequência de um nome ao longo das décadas |
| `ranking_nomes` | Ranking dos nomes mais populares do Brasil |
| `consultar_agregado` | Consulta dados agregados (população, PIB, área) |
| `listar_pesquisas` | Lista pesquisas e agregados disponíveis |
| `obter_malha` | Obtém metadados geográficos de uma região |
| `buscar_cnae` | Busca informações da CNAE (atividades econômicas) |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `estados_brasileiros` | Lista dos 27 estados com sigla, nome e região |
| `regioes_brasileiras` | As 5 macro-regiões com quantidade de estados |
| `niveis_territoriais` | Referência dos níveis territoriais e códigos de API |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `resumo_estado` | Resumo analítico completo de um estado |
| `comparativo_regional` | Comparação entre as 5 macro-regiões |

---

## Jurisprudência

Tribunais Superiores (STF, STJ, TST) — jurisprudência, súmulas, repercussão geral.

### Tools (6)

| Tool | Descrição |
|------|-----------|
| `buscar_jurisprudencia_stf` | Busca jurisprudência no STF |
| `buscar_jurisprudencia_stj` | Busca jurisprudência no STJ |
| `buscar_jurisprudencia_tst` | Busca jurisprudência no TST |
| `buscar_sumulas` | Busca súmulas dos tribunais superiores |
| `buscar_repercussao_geral` | Busca temas de repercussão geral do STF |
| `buscar_informativos` | Busca informativos de jurisprudência |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `tribunais_superiores` | Informações sobre STF, STJ e TST |
| `operadores_busca` | Operadores de busca disponíveis por tribunal |
| `info_api` | Informações gerais sobre as APIs de jurisprudência |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `pesquisa_jurisprudencial` | Pesquisa jurisprudencial completa sobre um tema |
| `analise_tema` | Análise de tema de repercussão geral do STF |

---

## Senado

Senado Federal — senadores, matérias, votações, comissões, agenda.

### Tools (22)

| Tool | Descrição |
|------|-----------|
| `listar_senadores` | Lista todos os senadores em exercício |
| `buscar_senador` | Busca detalhes de um senador pelo código |
| `buscar_senador_por_nome` | Busca senadores em exercício pelo nome |
| `votacoes_senador` | Consulta votações em que um senador participou |
| `buscar_materia` | Busca matérias legislativas (PEC, PLS, PLC, MPV) |
| `detalhe_materia` | Obtém detalhes de uma matéria pelo código |
| `consultar_tramitacao_materia` | Consulta tramitação de uma matéria |
| `textos_materia` | Lista textos e documentos de uma matéria |
| `votos_materia` | Consulta votações de uma matéria |
| `listar_votacoes` | Lista votações do plenário em um ano |
| `detalhe_votacao` | Detalhes de uma votação incluindo placar |
| `votacoes_recentes` | Lista votações em uma data específica |
| `listar_comissoes` | Lista comissões do Senado |
| `detalhe_comissao` | Detalhes de uma comissão |
| `membros_comissao` | Lista membros de uma comissão |
| `reunioes_comissao` | Lista reuniões de uma comissão |
| `agenda_plenario` | Agenda do plenário para um mês |
| `agenda_comissoes` | Agenda de comissões para uma data |
| `legislatura_atual` | Informações da legislatura atual |
| `partidos_senado` | Lista partidos com representação |
| `ufs_senado` | Lista UFs com representação |
| `tipos_materia` | Lista tipos de matéria legislativa |

### Resources (3)

| Resource | Descrição |
|----------|-----------|
| `tipos_materia` | Tipos de matéria legislativa com siglas e descrições |
| `info_api` | Informações gerais sobre a API do Senado |
| `comissoes_permanentes` | Comissões permanentes do Senado |

### Prompts (3)

| Prompt | Descrição |
|--------|-----------|
| `acompanhar_materia` | Acompanhamento completo de uma matéria legislativa |
| `perfil_senador` | Perfil completo de um senador |
| `analise_votacao_senado` | Análise detalhada de uma votação |

---

## TransfereGov

Transferências especiais (emendas pix) — API PostgREST pública.

### Tools (5)

| Tool | Descrição |
|------|-----------|
| `buscar_emendas_pix` | Lista transferências especiais (emendas pix) |
| `buscar_emenda_por_autor` | Busca emendas pix por nome do parlamentar |
| `detalhe_emenda` | Detalha uma emenda pix por ID do plano de ação |
| `emendas_por_municipio` | Busca emendas pix destinadas a um município |
| `resumo_emendas_ano` | Lista emendas pix de um ano para visão geral |

### Resources (1)

| Resource | Descrição |
|----------|-----------|
| `info_api` | Informações sobre a API do TransfereGov |

### Prompts (1)

| Prompt | Descrição |
|--------|-----------|
| `analise_emendas_pix` | Análise de emendas pix de um ano |

---

## Transparência

Portal da Transparência — contratos, despesas, servidores, emendas, sanções, benefícios sociais.

### Tools (18)

| Tool | Descrição |
|------|-----------|
| `buscar_contratos` | Busca contratos federais por CPF ou CNPJ |
| `consultar_despesas` | Consulta despesas e recursos recebidos por favorecido |
| `buscar_servidores` | Busca servidores públicos federais por CPF ou nome |
| `buscar_licitacoes` | Busca licitações federais por órgão e/ou período |
| `consultar_bolsa_familia` | Consulta dados do Bolsa Família por município ou NIS |
| `buscar_sancoes` | Busca sanções em bases federais (CEIS, CNEP, CEPIM, CEAF) |
| `buscar_emendas` | Busca emendas parlamentares por ano e/ou autor |
| `consultar_viagens` | Consulta viagens a serviço de servidor federal |
| `buscar_convenios` | Busca convênios e transferências voluntárias |
| `buscar_cartoes_pagamento` | Busca pagamentos com cartão corporativo |
| `buscar_pep` | Busca Pessoas Expostas Politicamente (PEP) |
| `buscar_acordos_leniencia` | Busca acordos de leniência (anticorrupção) |
| `buscar_notas_fiscais` | Busca notas fiscais eletrônicas vinculadas a gastos federais |
| `consultar_beneficio_social` | Consulta benefícios sociais (BPC, seguro-desemprego) por CPF/NIS |
| `consultar_cpf` | Consulta vínculos e benefícios de uma pessoa por CPF |
| `consultar_cnpj` | Consulta sanções e contratos de pessoa jurídica por CNPJ |
| `detalhar_contrato` | Detalha um contrato federal específico por ID |
| `detalhar_servidor` | Detalha um servidor público federal por ID |

### Resources (4)

| Resource | Descrição |
|----------|-----------|
| `endpoints_disponiveis` | Lista de todos os endpoints disponíveis |
| `bases_sancoes` | As 4 bases de sanções federais (CEIS, CNEP, CEPIM, CEAF) |
| `categorias_beneficios` | Tipos de benefícios sociais disponíveis |
| `info_api` | Informações gerais sobre a API do Portal da Transparência |

### Prompts (3)

| Prompt | Descrição |
|--------|-----------|
| `auditoria_fornecedor` | Auditoria completa de um fornecedor do governo federal |
| `analise_despesas` | Análise de despesas do governo em um período |
| `verificacao_compliance` | Verificação nas bases de sanções federais |

---

## TSE

Tribunal Superior Eleitoral — eleições, candidatos, prestação de contas.

### Tools (8)

| Tool | Descrição |
|------|-----------|
| `anos_eleitorais` | Lista anos com dados eleitorais disponíveis |
| `listar_eleicoes` | Lista eleições ordinárias registradas |
| `listar_eleicoes_suplementares` | Lista eleições suplementares de um estado/ano |
| `listar_estados_suplementares` | Lista estados com eleições suplementares |
| `listar_cargos` | Lista cargos disponíveis em um município |
| `listar_candidatos` | Lista candidatos para um cargo em um município |
| `buscar_candidato` | Busca detalhes completos de um candidato |
| `consultar_prestacao_contas` | Consulta prestação de contas de campanha |

### Resources (2)

| Resource | Descrição |
|----------|-----------|
| `cargos_eleitorais` | Códigos de cargos eleitorais |
| `info_api` | Informações gerais sobre a API do TSE |

### Prompts (2)

| Prompt | Descrição |
|--------|-----------|
| `analise_candidato` | Análise completa de um candidato |
| `comparativo_eleicao` | Comparativo entre candidatos de uma eleição |
