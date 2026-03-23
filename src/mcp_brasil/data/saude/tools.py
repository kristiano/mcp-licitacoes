"""Tool functions for the Saúde feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_number_br, markdown_table

from . import client


async def buscar_estabelecimentos(
    ctx: Context,
    codigo_municipio: str | None = None,
    codigo_uf: str | None = None,
    status: int | None = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """Busca estabelecimentos de saúde cadastrados no CNES/DataSUS.

    Consulta o Cadastro Nacional de Estabelecimentos de Saúde para encontrar
    hospitais, UBS, clínicas e outros estabelecimentos. Filtre por município
    ou UF para resultados mais relevantes.

    Args:
        codigo_municipio: Código IBGE do município (ex: "355030" para São Paulo).
        codigo_uf: Código IBGE do estado (ex: "35" para SP, "33" para RJ).
        status: 1 para ativos, 0 para inativos. Se omitido, retorna todos.
        limit: Número máximo de resultados (padrão: 20, máximo: 100).
        offset: Deslocamento para paginação (padrão: 0).

    Returns:
        Tabela com estabelecimentos encontrados.
    """
    filtro = codigo_municipio or codigo_uf or "Brasil"
    await ctx.info(f"Buscando estabelecimentos de saúde em {filtro}...")

    resultados = await client.buscar_estabelecimentos(
        codigo_municipio=codigo_municipio,
        codigo_uf=codigo_uf,
        status=status,
        limit=limit,
        offset=offset,
    )

    if not resultados:
        return "Nenhum estabelecimento encontrado para os filtros informados."

    rows = [
        (
            e.codigo_cnes or "—",
            e.nome_fantasia or e.nome_razao_social or "—",
            e.descricao_tipo or "—",
            e.tipo_gestao or "—",
            e.endereco or "—",
        )
        for e in resultados
    ]

    header = f"**Estabelecimentos de saúde** ({len(resultados)} resultados)\n\n"
    return header + markdown_table(["CNES", "Nome", "Tipo", "Gestão", "Endereço"], rows)


async def buscar_profissionais(
    ctx: Context,
    codigo_municipio: str | None = None,
    cnes: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """Busca profissionais de saúde cadastrados no CNES/DataSUS.

    Consulta profissionais vinculados a estabelecimentos de saúde.
    Filtre por município ou código CNES do estabelecimento.

    Args:
        codigo_municipio: Código IBGE do município (ex: "355030").
        cnes: Código CNES do estabelecimento (ex: "1234567").
        limit: Número máximo de resultados (padrão: 20, máximo: 100).
        offset: Deslocamento para paginação (padrão: 0).

    Returns:
        Tabela com profissionais encontrados.
    """
    filtro = cnes or codigo_municipio or "Brasil"
    await ctx.info(f"Buscando profissionais de saúde em {filtro}...")

    resultados = await client.buscar_profissionais(
        codigo_municipio=codigo_municipio,
        cnes=cnes,
        limit=limit,
        offset=offset,
    )

    if not resultados:
        return "Nenhum profissional encontrado para os filtros informados."

    rows = [
        (
            p.codigo_cnes or "—",
            p.nome or "—",
            p.cbo or "—",
            p.descricao_cbo or "—",
        )
        for p in resultados
    ]

    header = f"**Profissionais de saúde** ({len(resultados)} resultados)\n\n"
    return header + markdown_table(["CNES", "Nome", "CBO", "Ocupação"], rows)


async def listar_tipos_estabelecimento(ctx: Context) -> str:
    """Lista todos os tipos de estabelecimento de saúde do CNES.

    Retorna a tabela de tipos (código e descrição) usados na classificação
    dos estabelecimentos de saúde do SUS, como hospitais, UBS, CAPS, etc.

    Returns:
        Tabela com todos os tipos de estabelecimento.
    """
    await ctx.info("Listando tipos de estabelecimento de saúde...")

    resultados = await client.listar_tipos_estabelecimento()

    if not resultados:
        return "Nenhum tipo de estabelecimento encontrado."

    rows = [(t.codigo or "—", t.descricao or "—") for t in resultados]

    header = f"**Tipos de estabelecimento de saúde** ({len(resultados)} tipos)\n\n"
    return header + markdown_table(["Código", "Descrição"], rows)


async def consultar_leitos(
    ctx: Context,
    codigo_municipio: str | None = None,
    cnes: str | None = None,
    limit: int = 20,
    offset: int = 0,
) -> str:
    """Consulta leitos hospitalares cadastrados no CNES/DataSUS.

    Retorna dados sobre leitos existentes e leitos SUS por estabelecimento,
    incluindo tipo de leito e especialidade. Útil para análise de capacidade
    hospitalar de uma região.

    Args:
        codigo_municipio: Código IBGE do município (ex: "355030").
        cnes: Código CNES do estabelecimento (ex: "1234567").
        limit: Número máximo de resultados (padrão: 20, máximo: 100).
        offset: Deslocamento para paginação (padrão: 0).

    Returns:
        Tabela com leitos hospitalares encontrados.
    """
    filtro = cnes or codigo_municipio or "Brasil"
    await ctx.info(f"Consultando leitos hospitalares em {filtro}...")

    resultados = await client.consultar_leitos(
        codigo_municipio=codigo_municipio,
        cnes=cnes,
        limit=limit,
        offset=offset,
    )

    if not resultados:
        return "Nenhum leito encontrado para os filtros informados."

    total_existente = sum(leito.existente or 0 for leito in resultados)
    total_sus = sum(leito.sus or 0 for leito in resultados)

    rows = [
        (
            leito.codigo_cnes or "—",
            leito.tipo_leito or "—",
            leito.especialidade or "—",
            format_number_br(float(leito.existente), 0) if leito.existente is not None else "—",
            format_number_br(float(leito.sus), 0) if leito.sus is not None else "—",
        )
        for leito in resultados
    ]

    header = (
        f"**Leitos hospitalares** ({len(resultados)} registros)\n"
        f"Total existentes: {format_number_br(float(total_existente), 0)} | "
        f"Total SUS: {format_number_br(float(total_sus), 0)}\n\n"
    )
    return header + markdown_table(["CNES", "Tipo", "Especialidade", "Existentes", "SUS"], rows)
