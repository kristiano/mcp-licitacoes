"""Tool functions for the Dados Abertos feature."""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import markdown_table

from . import client


async def buscar_conjuntos(texto: str, ctx: Context, pagina: int = 1) -> str:
    """Busca conjuntos de dados abertos do governo federal.

    Pesquisa no catálogo do Portal Dados Abertos (dados.gov.br).
    Inclui datasets de saúde, educação, meio ambiente, economia e mais.

    Args:
        texto: Termo de busca (nome, tema ou palavra-chave do dataset).
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de datasets encontrados com título, organização e temas.
    """
    await ctx.info(f"Buscando conjuntos de dados '{texto}'...")
    resultado = await client.buscar_conjuntos(query=texto, pagina=pagina)
    await ctx.info(f"{resultado.total} conjuntos encontrados")

    if not resultado.conjuntos:
        return f"Nenhum conjunto de dados encontrado para '{texto}'."

    lines = [f"**Total:** {resultado.total} conjuntos de dados\n"]
    for i, c in enumerate(resultado.conjuntos, 1):
        temas = ", ".join(c.temas[:3]) if c.temas else "N/A"
        lines.extend(
            [
                f"### {i}. {c.titulo or 'Sem título'}",
                f"**ID:** `{c.id}`" if c.id else "",
                f"**Organização:** {c.organizacao_nome or 'N/A'}",
                f"**Temas:** {temas}",
                f"**Atualizado:** {c.data_atualizacao or 'N/A'}",
                "",
            ]
        )

    if resultado.total > len(resultado.conjuntos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)


async def detalhar_conjunto(conjunto_id: str, ctx: Context) -> str:
    """Obtém detalhes completos de um conjunto de dados do Portal Dados Abertos.

    Retorna título, descrição, organização, temas, tags e datas.
    Use buscar_conjuntos() para encontrar o ID do dataset.

    Args:
        conjunto_id: ID do conjunto de dados.

    Returns:
        Detalhes completos do dataset.
    """
    await ctx.info(f"Detalhando conjunto {conjunto_id}...")
    conjunto = await client.detalhar_conjunto(conjunto_id)

    if not conjunto:
        return f"Conjunto de dados '{conjunto_id}' não encontrado."

    temas = ", ".join(conjunto.temas) if conjunto.temas else "N/A"
    tags = ", ".join(conjunto.tags) if conjunto.tags else "N/A"
    desc = (conjunto.descricao or "Sem descrição")[:500]

    lines = [
        f"**{conjunto.titulo or 'Sem título'}**",
        f"\n{desc}",
        f"\n**Organização:** {conjunto.organizacao_nome or 'N/A'}",
        f"**Temas:** {temas}",
        f"**Tags:** {tags}",
        f"**Criado em:** {conjunto.data_criacao or 'N/A'}",
        f"**Atualizado em:** {conjunto.data_atualizacao or 'N/A'}",
        f"\n_Use buscar_recursos(conjunto_id='{conjunto_id}') para ver os arquivos disponíveis._",
    ]
    return "\n".join(lines)


async def listar_organizacoes(ctx: Context, pagina: int = 1) -> str:
    """Lista organizações que publicam dados no Portal Dados Abertos.

    Retorna ministérios, autarquias e órgãos que disponibilizam datasets.

    Args:
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de organizações com nome e quantidade de datasets.
    """
    await ctx.info("Listando organizações...")
    resultado = await client.listar_organizacoes(pagina=pagina)
    await ctx.info(f"{resultado.total} organizações encontradas")

    if not resultado.organizacoes:
        return "Nenhuma organização encontrada."

    rows = [(o.nome or "N/A", str(o.total_conjuntos or 0)) for o in resultado.organizacoes]
    header = f"**Total:** {resultado.total} organizações\n\n"
    table = markdown_table(["Organização", "Datasets"], rows)

    footer = ""
    if resultado.total > len(resultado.organizacoes):
        footer = f"\n\n*Use pagina={pagina + 1} para mais resultados.*"
    return header + table + footer


async def buscar_recursos(conjunto_id: str, ctx: Context, pagina: int = 1) -> str:
    """Lista os recursos (arquivos e APIs) de um conjunto de dados.

    Cada dataset pode ter múltiplos recursos em diferentes formatos
    (CSV, JSON, XML, etc.) e links de download.

    Args:
        conjunto_id: ID do conjunto de dados.
        pagina: Página de resultados (padrão 1).

    Returns:
        Lista de recursos com formato, título e link de download.
    """
    await ctx.info(f"Buscando recursos do conjunto {conjunto_id}...")
    resultado = await client.buscar_recursos(conjunto_id=conjunto_id, pagina=pagina)
    await ctx.info(f"{resultado.total} recursos encontrados")

    if not resultado.recursos:
        return f"Nenhum recurso encontrado para o conjunto '{conjunto_id}'."

    lines = [f"**Total:** {resultado.total} recursos\n"]
    for i, r in enumerate(resultado.recursos, 1):
        lines.extend(
            [
                f"### {i}. {r.titulo or 'Sem título'}",
                f"**Formato:** {r.formato or 'N/A'}",
                f"**Descrição:** {(r.descricao or 'N/A')[:200]}",
            ]
        )
        if r.link:
            lines.append(f"[Download]({r.link})")
        lines.append("")

    if resultado.total > len(resultado.recursos):
        lines.append(f"*Use pagina={pagina + 1} para mais resultados.*")
    return "\n".join(lines)
