"""Prompts for the TSE feature — analysis templates for LLMs."""

from __future__ import annotations


def analise_candidato(
    nome: str,
    ano: int,
    municipio: int,
    eleicao_id: int,
    cargo: int,
) -> str:
    """Gera uma análise completa de um candidato.

    Orienta o LLM a consultar dados do candidato, patrimônio e prestação de contas.

    Args:
        nome: Nome do candidato para buscar.
        ano: Ano da eleição.
        municipio: Código do município.
        eleicao_id: ID da eleição.
        cargo: Código do cargo.
    """
    return (
        f"Faça uma análise completa do candidato '{nome}' "
        f"na eleição {ano} usando os dados do TSE.\n\n"
        "Passos:\n"
        f"1. Use listar_candidatos(ano={ano}, municipio={municipio}, "
        f"eleicao_id={eleicao_id}, cargo={cargo}) para encontrar o candidato\n"
        "2. Com o ID do candidato, use buscar_candidato() para detalhes completos\n"
        "3. Use consultar_prestacao_contas() para ver as finanças de campanha\n\n"
        "Apresente:\n"
        "- Dados pessoais e eleitorais\n"
        "- Patrimônio declarado (total de bens)\n"
        "- Receitas e despesas de campanha\n"
        "- Principais doadores e fornecedores\n"
        "- Situação da candidatura (apto/inapto, ficha limpa)"
    )


def comparativo_eleicao(ano: int, municipio: int, eleicao_id: int, cargo: int) -> str:
    """Gera um comparativo entre candidatos de uma eleição.

    Args:
        ano: Ano da eleição.
        municipio: Código do município.
        eleicao_id: ID da eleição.
        cargo: Código do cargo.
    """
    return (
        f"Compare os candidatos da eleição {ano} usando os dados do TSE.\n\n"
        "Passos:\n"
        f"1. Use listar_candidatos(ano={ano}, municipio={municipio}, "
        f"eleicao_id={eleicao_id}, cargo={cargo})\n"
        "2. Para cada candidato, use buscar_candidato() para detalhes\n"
        "3. Para cada candidato, use consultar_prestacao_contas()\n\n"
        "Apresente uma tabela comparativa com:\n"
        "- Nome, partido, número\n"
        "- Patrimônio declarado\n"
        "- Receitas e despesas de campanha\n"
        "- Situação (apto/inapto)\n"
        "- Escolaridade e ocupação"
    )
