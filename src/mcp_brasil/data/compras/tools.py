"""Tool functions for the Compras feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import format_brl

from . import client
from .constants import MODALIDADES


async def buscar_contratacoes(
    texto: str,
    ctx: Context,
    cnpj_orgao: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca licitações e contratações públicas no PNCP.

    Pesquisa no Portal Nacional de Contratações Públicas (Lei 14.133/2021).
    Cobre contratações federais, estaduais e municipais.

    Args:
        texto: Termo de busca (nome de empresa, produto, serviço ou CNPJ).
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        data_inicial: Data inicial DD/MM/YYYY (opcional).
        data_final: Data final DD/MM/YYYY (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de contratações encontradas com objeto, valor e situação.
    """
    await ctx.info(f"Buscando contratações '{texto}'...")
    resultado = await client.buscar_contratacoes(
        query=texto,
        cnpj_orgao=cnpj_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} contratações encontradas")

    if not resultado.contratacoes:
        return f"Nenhuma contratação encontrada para '{texto}'."

    lines = [f"**Total:** {resultado.total} contratações\n"]
    for i, c in enumerate(resultado.contratacoes, 1):
        modalidade = MODALIDADES.get(c.modalidade_id or 0, c.modalidade_nome or "N/A")
        valor_est = format_brl(c.valor_estimado) if c.valor_estimado else "N/A"
        valor_hom = format_brl(c.valor_homologado) if c.valor_homologado else "N/A"
        lines.extend(
            [
                f"### {i}. {c.objeto or 'Sem descrição'}",
                f"**Órgão:** {c.orgao_nome or 'N/A'} ({c.orgao_cnpj or 'N/A'})",
                f"**Modalidade:** {modalidade}",
                f"**Situação:** {c.situacao_nome or 'N/A'}",
                f"**Valor estimado:** {valor_est} | **Homologado:** {valor_hom}",
                f"**Publicação:** {c.data_publicacao or 'N/A'}",
                f"**Local:** {c.municipio or 'N/A'}/{c.uf or 'N/A'} ({c.esfera or 'N/A'})",
            ]
        )
        if c.link_pncp:
            lines.append(f"[Ver no PNCP]({c.link_pncp})")
        lines.append("")

    if resultado.total > len(resultado.contratacoes):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_contratos(
    ctx: Context,
    texto: str | None = None,
    cnpj_fornecedor: str | None = None,
    cnpj_orgao: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca contratos públicos no PNCP.

    Permite buscar por texto livre, CNPJ do fornecedor ou do órgão contratante.
    Pelo menos um filtro deve ser informado.

    Args:
        texto: Termo de busca (opcional).
        cnpj_fornecedor: CNPJ do fornecedor (opcional).
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        data_inicial: Data inicial DD/MM/YYYY (opcional).
        data_final: Data final DD/MM/YYYY (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de contratos encontrados.
    """
    if not any([texto, cnpj_fornecedor, cnpj_orgao, data_inicial]):
        return "Informe pelo menos um filtro: texto, cnpj_fornecedor, cnpj_orgao ou data_inicial."

    desc = texto or cnpj_fornecedor or cnpj_orgao or "contratos"
    await ctx.info(f"Buscando contratos '{desc}'...")
    resultado = await client.buscar_contratos(
        query=texto,
        cnpj_fornecedor=cnpj_fornecedor,
        cnpj_orgao=cnpj_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} contratos encontrados")

    if not resultado.contratos:
        return f"Nenhum contrato encontrado para '{desc}'."

    lines = [f"**Total:** {resultado.total} contratos\n"]
    for i, c in enumerate(resultado.contratos, 1):
        raw_valor = c.valor_final or c.valor_inicial
        valor = format_brl(raw_valor) if raw_valor else "N/A"
        lines.extend(
            [
                f"### {i}. {c.objeto or 'Sem descrição'}",
                f"**Órgão:** {c.orgao_nome or 'N/A'}",
                f"**Fornecedor:** {c.fornecedor_nome or 'N/A'} ({c.fornecedor_cnpj or 'N/A'})",
                f"**Contrato nº:** {c.numero_contrato or 'N/A'}",
                f"**Valor:** {valor}",
                f"**Vigência:** {c.vigencia_inicio or 'N/A'} a {c.vigencia_fim or 'N/A'}",
                f"**Situação:** {c.situacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.contratos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def buscar_atas(
    ctx: Context,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca atas de registro de preço no PNCP.

    Atas de registro de preço são documentos que registram preços praticados
    em licitações para aquisições futuras.

    Args:
        texto: Termo de busca (opcional).
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        data_inicial: Data inicial DD/MM/YYYY (opcional).
        data_final: Data final DD/MM/YYYY (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de atas de registro de preço encontradas.
    """
    if not any([texto, cnpj_orgao, data_inicial]):
        return "Informe pelo menos um filtro: texto, cnpj_orgao ou data_inicial."

    desc = texto or cnpj_orgao or "atas"
    await ctx.info(f"Buscando atas de registro de preço '{desc}'...")
    resultado = await client.buscar_atas(
        query=texto,
        cnpj_orgao=cnpj_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
    await ctx.info(f"{resultado.total} atas encontradas")

    if not resultado.atas:
        return f"Nenhuma ata de registro de preço encontrada para '{desc}'."

    lines = [f"**Total:** {resultado.total} atas\n"]
    for i, a in enumerate(resultado.atas, 1):
        valor = format_brl(a.valor_total) if a.valor_total else "N/A"
        lines.extend(
            [
                f"### {i}. {a.objeto or 'Sem descrição'}",
                f"**Órgão:** {a.orgao_nome or 'N/A'}",
                f"**Fornecedor:** {a.fornecedor_nome or 'N/A'} ({a.fornecedor_cnpj or 'N/A'})",
                f"**Ata nº:** {a.numero_ata or 'N/A'}",
                f"**Valor total:** {valor}",
                f"**Vigência:** {a.vigencia_inicio or 'N/A'} a {a.vigencia_fim or 'N/A'}",
                f"**Situação:** {a.situacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.atas):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def consultar_fornecedor(cnpj: str, ctx: Context) -> str:
    """Consulta informações de um fornecedor de contratações públicas pelo CNPJ.

    Retorna dados cadastrais do fornecedor no PNCP (Portal Nacional de
    Contratações Públicas).

    Args:
        cnpj: CNPJ do fornecedor (com ou sem formatação).

    Returns:
        Dados do fornecedor encontrado.
    """
    await ctx.info(f"Consultando fornecedor CNPJ {cnpj}...")
    resultado = await client.consultar_fornecedor(cnpj=cnpj)
    await ctx.info(f"{resultado.total} fornecedor(es) encontrado(s)")

    if not resultado.fornecedores:
        return f"Nenhum fornecedor encontrado com CNPJ {cnpj}."

    lines: list[str] = []
    for f in resultado.fornecedores:
        lines.extend(
            [
                f"**{f.razao_social or 'N/A'}**",
                f"**CNPJ:** {f.cnpj or 'N/A'}",
                f"**Nome fantasia:** {f.nome_fantasia or 'N/A'}",
                f"**Local:** {f.municipio or 'N/A'}/{f.uf or 'N/A'}",
                f"**Porte:** {f.porte or 'N/A'}",
                f"**Abertura:** {f.data_abertura or 'N/A'}",
                "",
            ]
        )
    return "\n".join(lines)


async def buscar_itens(
    ctx: Context,
    texto: str | None = None,
    cnpj_orgao: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca itens de contratações públicas no PNCP.

    Pesquisa materiais e serviços adquiridos em contratações públicas.
    Pelo menos um filtro deve ser informado.

    Args:
        texto: Termo de busca (descrição do item).
        cnpj_orgao: CNPJ do órgão contratante (opcional).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de itens encontrados com descrição, quantidade e valor.
    """
    if not any([texto, cnpj_orgao]):
        return "Informe pelo menos um filtro: texto ou cnpj_orgao."

    desc = texto or cnpj_orgao or "itens"
    await ctx.info(f"Buscando itens '{desc}'...")
    resultado = await client.buscar_itens(query=texto, cnpj_orgao=cnpj_orgao, pagina=pagina)
    await ctx.info(f"{resultado.total} itens encontrados")

    if not resultado.itens:
        return f"Nenhum item encontrado para '{desc}'."

    lines = [f"**Total:** {resultado.total} itens\n"]
    for i, item in enumerate(resultado.itens, 1):
        valor_unit = format_brl(item.valor_unitario) if item.valor_unitario else "N/A"
        valor_total = format_brl(item.valor_total) if item.valor_total else "N/A"
        lines.extend(
            [
                f"### {i}. {item.descricao or 'Sem descrição'}",
                f"**Item nº:** {item.numero_item or 'N/A'}",
                f"**Quantidade:** {item.quantidade or 'N/A'} {item.unidade_medida or ''}".rstrip(),
                f"**Valor unitário:** {valor_unit} | **Total:** {valor_total}",
                f"**Situação:** {item.situacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.itens):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def consultar_orgao(
    ctx: Context,
    texto: str | None = None,
    uf: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca órgãos contratantes no PNCP.

    Pesquisa órgãos públicos que realizam contratações. Útil para
    encontrar o CNPJ de um órgão específico para filtrar outras buscas.

    Args:
        texto: Nome do órgão (parcial ou completo).
        uf: UF do órgão (ex: SP, RJ, DF).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de órgãos encontrados.
    """
    if not any([texto, uf]):
        return "Informe pelo menos um filtro: texto ou uf."

    desc = texto or uf or "órgãos"
    await ctx.info(f"Buscando órgãos '{desc}'...")
    resultado = await client.consultar_orgao(query=texto, uf=uf, pagina=pagina)
    await ctx.info(f"{resultado.total} órgãos encontrados")

    if not resultado.orgaos:
        return f"Nenhum órgão encontrado para '{desc}'."

    lines = [f"**Total:** {resultado.total} órgãos\n"]
    for i, o in enumerate(resultado.orgaos, 1):
        lines.extend(
            [
                f"### {i}. {o.razao_social or 'N/A'}",
                f"**CNPJ:** {o.cnpj or 'N/A'}",
                f"**Esfera:** {o.esfera or 'N/A'} | **Poder:** {o.poder or 'N/A'}",
                f"**Local:** {o.municipio or 'N/A'}/{o.uf or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.orgaos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)
