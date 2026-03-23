"""Tool functions for the Diário Oficial feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

import re

from fastmcp import Context

from mcp_brasil._shared.formatting import markdown_table

from . import client

_HTML_TAG_RE = re.compile(r"<[^>]+>")


async def buscar_diarios(
    texto: str,
    ctx: Context,
    territorio_id: str | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    pagina: int = 0,
) -> str:
    """Busca em diários oficiais municipais por texto livre.

    Pesquisa full-text em diários oficiais de 5.000+ municípios brasileiros.
    Útil para encontrar menções a empresas, pessoas, contratos, licitações,
    nomeações, exonerações e atos administrativos.

    Args:
        texto: Termo de busca (nome de empresa, CNPJ, pessoa, palavra-chave).
        territorio_id: Código IBGE do município (opcional, ex: 3550308 para São Paulo).
        data_inicio: Data inicial no formato YYYY-MM-DD (opcional).
        data_fim: Data final no formato YYYY-MM-DD (opcional).
        pagina: Página de resultados (0-indexada, padrão 0).

    Returns:
        Lista de diários oficiais com trechos relevantes.
    """
    await ctx.info(f"Buscando diários oficiais para '{texto}'...")
    resultado = await client.buscar_diarios(
        querystring=texto,
        territory_id=territorio_id,
        since=data_inicio,
        until=data_fim,
        offset=pagina * 10,
    )
    await ctx.info(f"{resultado.total_gazettes} diários encontrados")

    if not resultado.gazettes:
        return f"Nenhum diário oficial encontrado para '{texto}'."

    lines = [f"**Total:** {resultado.total_gazettes} diários encontrados\n"]
    for i, d in enumerate(resultado.gazettes[:10], 1):
        lines.append(f"### {i}. {d.territory_name or 'N/A'}/{d.state_code or '??'}")
        lines.append(f"**Data:** {d.date or 'N/A'} | **Edição:** {d.edition_number or 'N/A'}")
        if d.is_extra_edition:
            lines.append("**Edição Extra**")
        if d.excerpts:
            excerpt = _HTML_TAG_RE.sub("", d.excerpts[0])[:500]
            lines.append(f"\n> {excerpt}...")
        if d.txt_url:
            lines.append(f"\n[Texto completo]({d.txt_url})")
        lines.append("")

    if resultado.total_gazettes > 10:
        lines.append(
            f"\n*Mostrando 10 de {resultado.total_gazettes}. "
            f"Use pagina={pagina + 1} para mais resultados.*"
        )
    return "\n".join(lines)


async def buscar_trechos(
    territorio_id: str,
    texto: str,
    ctx: Context,
    data_inicio: str | None = None,
    data_fim: str | None = None,
    pagina: int = 0,
) -> str:
    """Busca excertos específicos em diários oficiais de um município.

    Retorna trechos individuais (recortes) de diários oficiais de um município
    específico. Diferente de buscar_diarios que retorna edições inteiras, esta
    ferramenta retorna excertos isolados com contexto.

    Use buscar_cidades() para obter o código IBGE do município (territorio_id).

    Args:
        territorio_id: Código IBGE do município (ex: 3550308 para São Paulo).
        texto: Termo de busca (nome, CNPJ, palavra-chave).
        data_inicio: Data inicial no formato YYYY-MM-DD (opcional).
        data_fim: Data final no formato YYYY-MM-DD (opcional).
        pagina: Página de resultados (0-indexada, padrão 0).

    Returns:
        Lista de excertos encontrados com data e conteúdo.
    """
    await ctx.info(f"Buscando trechos para '{texto}' no território {territorio_id}...")
    resultado = await client.buscar_trechos(
        territory_id=territorio_id,
        querystring=texto,
        since=data_inicio,
        until=data_fim,
        offset=pagina * 10,
    )
    await ctx.info(f"{resultado.total_excerpts} trechos encontrados")

    if not resultado.excerpts:
        return f"Nenhum trecho encontrado para '{texto}' no território {territorio_id}."

    lines = [f"**Total:** {resultado.total_excerpts} trechos encontrados\n"]
    for i, e in enumerate(resultado.excerpts[:10], 1):
        lines.append(f"### {i}. {e.territory_name or 'N/A'}/{e.state_code or '??'}")
        lines.append(f"**Data:** {e.date or 'N/A'} | **Edição:** {e.edition_number or 'N/A'}")
        if e.is_extra_edition:
            lines.append("**Edição Extra**")
        if e.subheadline:
            lines.append(f"**Seção:** {e.subheadline}")
        if e.excerpt:
            excerpt = _HTML_TAG_RE.sub("", e.excerpt)[:500]
            lines.append(f"\n> {excerpt}...")
        if e.txt_url:
            lines.append(f"\n[Texto completo]({e.txt_url})")
        lines.append("")

    if resultado.total_excerpts > 10:
        lines.append(
            f"\n*Mostrando 10 de {resultado.total_excerpts}. "
            f"Use pagina={pagina + 1} para mais resultados.*"
        )
    return "\n".join(lines)


async def buscar_cidades(nome: str, ctx: Context) -> str:
    """Busca municípios disponíveis no Querido Diário pelo nome.

    Retorna os códigos IBGE necessários para filtrar buscas por território.

    Args:
        nome: Nome (ou parte do nome) da cidade.

    Returns:
        Lista de cidades encontradas com código IBGE.
    """
    await ctx.info(f"Buscando cidades '{nome}'...")
    cidades = await client.buscar_cidades(nome)
    await ctx.info(f"{len(cidades)} cidades encontradas")

    if not cidades:
        return f"Nenhuma cidade encontrada para '{nome}'."

    rows = [(c.territory_id, c.territory_name, c.state_code) for c in cidades]
    return markdown_table(["Código IBGE", "Cidade", "UF"], rows)


async def listar_territorios(ctx: Context) -> str:
    """Lista todos os municípios com diários oficiais no Querido Diário.

    Retorna a lista completa de territórios disponíveis para busca.
    Use o código IBGE retornado para filtrar buscas em buscar_diarios.

    Returns:
        Lista de municípios disponíveis com código IBGE e UF.
    """
    await ctx.info("Listando territórios disponíveis...")
    cidades = await client.listar_cidades()
    await ctx.info(f"{len(cidades)} territórios disponíveis")

    rows = [(c.territory_id, c.territory_name, c.state_code) for c in cidades]
    header = f"**{len(cidades)} municípios** com diários oficiais disponíveis:\n\n"
    return header + markdown_table(["Código IBGE", "Cidade", "UF"], rows[:100])
