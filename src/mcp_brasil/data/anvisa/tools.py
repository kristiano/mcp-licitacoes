"""Tool functions for the ANVISA feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
    - Uses Context for structured logging and progress reporting
"""

from __future__ import annotations

from fastmcp import Context

from mcp_brasil._shared.formatting import markdown_table

from . import client
from .constants import SECOES_BULA


async def buscar_medicamento(
    ctx: Context,
    nome: str,
    pagina: int = 1,
) -> str:
    """Busca medicamentos no Bulário Eletrônico da ANVISA por nome comercial.

    Consulta o Bulário oficial da ANVISA para encontrar medicamentos registrados.
    Retorna nome, empresa, princípio ativo, categoria e número do registro.

    Args:
        nome: Nome comercial do medicamento (ex: "dipirona", "amoxicilina").
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com medicamentos encontrados.
    """
    await ctx.info(f"Buscando '{nome}' no Bulário ANVISA...")

    resultados = await client.buscar_medicamento(nome=nome, pagina=pagina)

    if not resultados:
        return (
            f"Nenhum medicamento encontrado para '{nome}' no Bulário ANVISA. "
            "Tente um nome diferente ou verifique a grafia."
        )

    rows = [
        (
            m.nome_produto or "—",
            m.principio_ativo or "—",
            m.razao_social or "—",
            m.categoria_regulatoria or "—",
            m.numero_processo or "—",
        )
        for m in resultados
    ]

    header = f"**Medicamentos ANVISA** ({len(resultados)} resultado(s) para '{nome}')\n\n"
    return header + markdown_table(
        ["Nome", "Princípio Ativo", "Empresa", "Categoria", "Nº Processo"], rows
    )


async def buscar_por_principio_ativo(
    ctx: Context,
    principio_ativo: str,
    pagina: int = 1,
) -> str:
    """Busca medicamentos por princípio ativo no Bulário da ANVISA.

    Encontra todos os medicamentos registrados que contêm um dado princípio ativo.
    Útil para comparar genéricos, similares e referência do mesmo princípio ativo.

    Args:
        principio_ativo: Nome do princípio ativo (ex: "losartana", "metformina").
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com medicamentos encontrados.
    """
    await ctx.info(f"Buscando princípio ativo '{principio_ativo}' no Bulário...")

    resultados = await client.buscar_por_principio_ativo(
        principio_ativo=principio_ativo, pagina=pagina
    )

    if not resultados:
        return (
            f"Nenhum medicamento com princípio ativo '{principio_ativo}' encontrado. "
            "Tente o nome completo ou verifique a grafia."
        )

    rows = [
        (
            m.nome_produto or "—",
            m.principio_ativo or "—",
            m.razao_social or "—",
            m.categoria_regulatoria or "—",
            m.numero_registro or "—",
        )
        for m in resultados
    ]

    header = (
        f"**Medicamentos com princípio ativo '{principio_ativo}'** "
        f"({len(resultados)} resultado(s))\n\n"
    )
    return header + markdown_table(
        ["Nome", "Princípio Ativo", "Empresa", "Categoria", "Registro"], rows
    )


async def consultar_bula(
    ctx: Context,
    numero_processo: str,
) -> str:
    """Consulta as bulas disponíveis de um medicamento pelo número do processo ANVISA.

    Retorna links para bulas do paciente e do profissional de saúde.
    Use buscar_medicamento() primeiro para obter o número do processo.

    Args:
        numero_processo: Número do processo ANVISA (obtido via buscar_medicamento).

    Returns:
        Lista de bulas disponíveis com links para download.
    """
    await ctx.info(f"Consultando bulas do processo {numero_processo}...")

    resultados = await client.consultar_bula(numero_processo=numero_processo)

    if not resultados:
        return (
            f"Nenhuma bula encontrada para o processo {numero_processo}. "
            "Verifique se o número do processo está correto."
        )

    lines = [f"**Bulas disponíveis** (processo {numero_processo}, {len(resultados)} bula(s))\n"]

    for bula in resultados:
        lines.append(f"- **{bula.nome_produto or 'Medicamento'}**")
        lines.append(f"  - Empresa: {bula.empresa or '—'}")
        lines.append(f"  - Tipo: {bula.tipo_bula or '—'}")
        lines.append(f"  - Publicação: {bula.data_publicacao or '—'}")
        if bula.url_bula:
            lines.append(f"  - URL: {bula.url_bula}")
        lines.append("")

    return "\n".join(lines)


async def listar_categorias(ctx: Context) -> str:
    """Lista as categorias regulatórias de medicamentos da ANVISA.

    Categorias incluem: Novo, Genérico, Similar, Biológico, Específico,
    Fitoterápico, Dinamizado e Radiofármaco. Cada medicamento registrado
    pertence a uma dessas categorias.

    Returns:
        Tabela com códigos e descrições das categorias.
    """
    await ctx.info("Listando categorias de medicamentos ANVISA...")

    categorias = client.listar_categorias()

    rows = [(c.codigo, c.descricao) for c in categorias]

    header = f"**Categorias de medicamentos ANVISA** ({len(categorias)} categorias)\n\n"
    return header + markdown_table(["Código", "Descrição"], rows)


async def informacoes_bula(ctx: Context) -> str:
    """Informa as seções padrão de uma bula de medicamento no Brasil.

    Útil para orientar o usuário sobre o que encontrar em uma bula e
    como interpretar as informações. Segue o padrão definido pela ANVISA.

    Returns:
        Lista das seções padrão de uma bula.
    """
    await ctx.info("Consultando estrutura padrão de bulas...")

    secoes_lista = "\n".join(f"{i + 1}. {secao}" for i, secao in enumerate(SECOES_BULA))

    return (
        "**Seções padrão de uma bula de medicamento (ANVISA)**\n\n"
        f"{secoes_lista}\n\n"
        "**Dica:** A bula do paciente tem linguagem simplificada. "
        "A bula do profissional tem informações técnicas detalhadas.\n"
        "Use buscar_medicamento() e consultar_bula() para acessar bulas específicas."
    )
