"""Tool functions for the Transparência feature.

Rules (ADR-001):
    - tools.py NEVER makes HTTP directly — delegates to client.py
    - Returns formatted strings for LLM consumption
"""

from __future__ import annotations

from mcp_brasil._shared.formatting import format_brl, markdown_table, truncate_list

from . import client


async def buscar_contratos(cpf_cnpj: str, pagina: int = 1) -> str:
    """Busca contratos federais por CPF ou CNPJ do fornecedor.

    Consulta o Portal da Transparência para listar contratos firmados
    com o governo federal por um fornecedor específico.

    Args:
        cpf_cnpj: CPF ou CNPJ do fornecedor (aceita com ou sem formatação).
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com contratos encontrados.
    """
    contratos = await client.buscar_contratos(cpf_cnpj, pagina)
    if not contratos:
        return f"Nenhum contrato encontrado para o CPF/CNPJ '{cpf_cnpj}'."

    rows = [
        (
            c.numero or "—",
            (c.objeto or "—")[:80],
            format_brl(c.valor_final) if c.valor_final else "—",
            c.data_inicio or "—",
            c.data_fim or "—",
            (c.orgao or "—")[:40],
        )
        for c in contratos
    ]
    header = f"Contratos do fornecedor {cpf_cnpj} (página {pagina}):\n\n"
    return header + markdown_table(
        ["Número", "Objeto", "Valor Final", "Início", "Fim", "Órgão"], rows
    )


async def consultar_despesas(
    mes_ano_inicio: str,
    mes_ano_fim: str,
    codigo_favorecido: str | None = None,
    pagina: int = 1,
) -> str:
    """Consulta despesas e recursos recebidos por favorecido.

    Mostra pagamentos realizados pelo governo federal a um favorecido
    (pessoa física ou jurídica) em um período.

    Args:
        mes_ano_inicio: Mês/ano de início no formato MM/AAAA (ex: 01/2024).
        mes_ano_fim: Mês/ano de fim no formato MM/AAAA (ex: 12/2024).
        codigo_favorecido: CPF ou CNPJ do favorecido (opcional).
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com despesas encontradas.
    """
    despesas = await client.consultar_despesas(
        mes_ano_inicio, mes_ano_fim, codigo_favorecido, pagina
    )
    if not despesas:
        return "Nenhuma despesa encontrada para os parâmetros informados."

    rows = [
        (
            f"{d.mes or '—'}/{d.ano or '—'}",
            (d.favorecido_nome or "—")[:50],
            format_brl(d.valor) if d.valor else "—",
            (d.orgao_nome or "—")[:40],
            d.uf or "—",
        )
        for d in despesas
    ]
    header = f"Despesas de {mes_ano_inicio} a {mes_ano_fim} (página {pagina}):\n\n"
    return header + markdown_table(["Período", "Favorecido", "Valor", "Órgão", "UF"], rows)


async def buscar_servidores(
    cpf: str | None = None,
    nome: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca servidores públicos federais por CPF ou nome.

    Consulta a base de servidores do Portal da Transparência.
    Informe CPF ou nome (pelo menos um é obrigatório).

    Args:
        cpf: CPF do servidor (opcional se nome fornecido).
        nome: Nome do servidor (opcional se CPF fornecido).
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com servidores encontrados.
    """
    if not cpf and not nome:
        return "Informe CPF ou nome do servidor para a busca."

    servidores = await client.buscar_servidores(cpf=cpf, nome=nome, pagina=pagina)
    if not servidores:
        busca = cpf or nome
        return f"Nenhum servidor encontrado para '{busca}'."

    rows = [
        (
            s.cpf or "—",
            (s.nome or "—")[:50],
            s.tipo_servidor or "—",
            s.situacao or "—",
            (s.orgao or "—")[:40],
        )
        for s in servidores
    ]
    busca = cpf or nome
    header = f"Servidores encontrados para '{busca}' (página {pagina}):\n\n"
    return header + markdown_table(["CPF", "Nome", "Tipo", "Situação", "Órgão"], rows)


async def buscar_licitacoes(
    codigo_orgao: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca licitações federais por órgão e/ou período.

    Consulta processos licitatórios do governo federal.
    Pelo menos um filtro (órgão ou datas) é recomendado.

    Args:
        codigo_orgao: Código SIAFI do órgão (ex: "26246" para UFPI).
        data_inicial: Data inicial no formato DD/MM/AAAA.
        data_final: Data final no formato DD/MM/AAAA.
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com licitações encontradas.
    """
    licitacoes = await client.buscar_licitacoes(
        codigo_orgao=codigo_orgao,
        data_inicial=data_inicial,
        data_final=data_final,
        pagina=pagina,
    )
    if not licitacoes:
        return "Nenhuma licitação encontrada para os parâmetros informados."

    rows = [
        (
            lc.numero or "—",
            (lc.objeto or "—")[:60],
            lc.modalidade or "—",
            lc.situacao or "—",
            format_brl(lc.valor_estimado) if lc.valor_estimado else "—",
            lc.data_abertura or "—",
        )
        for lc in licitacoes
    ]
    header = f"Licitações encontradas (página {pagina}):\n\n"
    return header + markdown_table(
        ["Número", "Objeto", "Modalidade", "Situação", "Valor Est.", "Abertura"], rows
    )


async def consultar_bolsa_familia(
    mes_ano: str,
    codigo_ibge: str | None = None,
    nis: str | None = None,
    pagina: int = 1,
) -> str:
    """Consulta dados do Novo Bolsa Família por município ou NIS.

    Informe código IBGE do município OU NIS do beneficiário.
    Retorna dados de pagamento do programa de transferência de renda.

    Args:
        mes_ano: Mês/ano de referência no formato AAAAMM (ex: 202401).
        codigo_ibge: Código IBGE do município (ex: 3550308 para São Paulo).
        nis: NIS (Número de Identificação Social) do beneficiário.
        pagina: Página de resultados (padrão: 1).

    Returns:
        Dados do Bolsa Família encontrados.
    """
    if not codigo_ibge and not nis:
        return "Informe o código IBGE do município ou o NIS do beneficiário."

    if nis:
        sacados = await client.consultar_bolsa_familia_nis(mes_ano, nis, pagina)
        if not sacados:
            return f"Nenhum dado encontrado para NIS '{nis}' em {mes_ano}."
        rows = [
            (
                s.nis or "—",
                (s.nome or "—")[:50],
                s.municipio or "—",
                s.uf or "—",
                format_brl(s.valor) if s.valor else "—",
            )
            for s in sacados
        ]
        return f"Bolsa Família — NIS {nis} ({mes_ano}):\n\n" + markdown_table(
            ["NIS", "Nome", "Município", "UF", "Valor"], rows
        )

    assert codigo_ibge is not None
    municipios = await client.consultar_bolsa_familia_municipio(mes_ano, codigo_ibge, pagina)
    if not municipios:
        return f"Nenhum dado encontrado para município {codigo_ibge} em {mes_ano}."
    rows = [
        (
            m.municipio or "—",
            m.uf or "—",
            str(m.quantidade) if m.quantidade else "—",
            format_brl(m.valor) if m.valor else "—",
            m.data_referencia or "—",
        )
        for m in municipios
    ]
    return f"Bolsa Família — Município {codigo_ibge} ({mes_ano}):\n\n" + markdown_table(
        ["Município", "UF", "Beneficiados", "Valor", "Referência"], rows
    )


async def buscar_sancoes(
    consulta: str,
    bases: list[str] | None = None,
    pagina: int = 1,
) -> str:
    """Busca sanções em bases federais (CEIS, CNEP, CEPIM, CEAF).

    Consulta simultânea nas bases de sanções do governo federal.
    Útil para due diligence, compliance e verificação anticorrupção.

    Bases disponíveis:
    - CEIS: Empresas Inidôneas e Suspensas
    - CNEP: Empresas Punidas (Lei Anticorrupção 12.846)
    - CEPIM: Entidades sem Fins Lucrativos Impedidas
    - CEAF: Expulsões da Administração Federal

    Args:
        consulta: CPF, CNPJ ou nome da pessoa/empresa a pesquisar.
        bases: Lista de bases (ex: ["ceis", "cnep"]). Padrão: todas.
        pagina: Página de resultados (padrão: 1).

    Returns:
        Sanções encontradas agrupadas por base.
    """
    sancoes = await client.buscar_sancoes(consulta, bases, pagina)
    if not sancoes:
        bases_str = ", ".join(bases) if bases else "CEIS, CNEP, CEPIM, CEAF"
        return f"Nenhuma sanção encontrada para '{consulta}' nas bases: {bases_str}."

    items: list[str] = []
    for s in sancoes:
        parts = [f"**{s.nome or '—'}** ({s.cpf_cnpj or '—'})"]
        parts.append(f"  Fonte: {s.fonte or '—'}")
        if s.tipo:
            parts.append(f"  Tipo: {s.tipo}")
        if s.orgao:
            parts.append(f"  Órgão sancionador: {s.orgao}")
        if s.data_inicio or s.data_fim:
            parts.append(f"  Período: {s.data_inicio or '—'} a {s.data_fim or '—'}")
        if s.fundamentacao:
            parts.append(f"  Fundamentação: {s.fundamentacao}")
        items.append("\n".join(parts))

    header = f"Sanções encontradas para '{consulta}' ({len(sancoes)} resultado(s)):\n\n"
    return header + truncate_list(items, max_items=30)


async def buscar_emendas(
    ano: int | None = None,
    nome_autor: str | None = None,
    pagina: int = 1,
) -> str:
    """Busca emendas parlamentares por ano e/ou autor.

    Consulta emendas individuais e de bancada ao orçamento federal.

    Args:
        ano: Ano da emenda (ex: 2024).
        nome_autor: Nome do parlamentar autor da emenda.
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com emendas encontradas.
    """
    emendas = await client.buscar_emendas(ano=ano, nome_autor=nome_autor, pagina=pagina)
    if not emendas:
        return "Nenhuma emenda encontrada para os parâmetros informados."

    rows = [
        (
            e.numero or "—",
            (e.autor or "—")[:40],
            e.tipo or "—",
            (e.localidade or "—")[:30],
            format_brl(e.valor_empenhado) if e.valor_empenhado else "—",
            format_brl(e.valor_pago) if e.valor_pago else "—",
        )
        for e in emendas
    ]
    header = f"Emendas parlamentares (página {pagina}):\n\n"
    return header + markdown_table(
        ["Número", "Autor", "Tipo", "Localidade", "Empenhado", "Pago"], rows
    )


async def consultar_viagens(cpf: str, pagina: int = 1) -> str:
    """Consulta viagens a serviço de servidor federal por CPF.

    Mostra viagens realizadas a serviço, incluindo diárias e passagens.

    Args:
        cpf: CPF do servidor (aceita com ou sem formatação).
        pagina: Página de resultados (padrão: 1).

    Returns:
        Tabela com viagens encontradas.
    """
    viagens = await client.consultar_viagens(cpf, pagina)
    if not viagens:
        return f"Nenhuma viagem encontrada para o CPF '{cpf}'."

    rows = [
        (
            (v.nome or "—")[:40],
            v.cargo or "—",
            (v.orgao or "—")[:30],
            v.destino or "—",
            f"{v.data_inicio or '—'} a {v.data_fim or '—'}",
            format_brl(v.valor_diarias) if v.valor_diarias else "—",
            format_brl(v.valor_passagens) if v.valor_passagens else "—",
        )
        for v in viagens
    ]
    header = f"Viagens do servidor CPF {cpf} (página {pagina}):\n\n"
    return header + markdown_table(
        ["Nome", "Cargo", "Órgão", "Destino", "Período", "Diárias", "Passagens"], rows
    )
