"""Analysis prompts for the Dados Abertos feature."""

from __future__ import annotations


def explorar_dados(tema: str) -> str:
    """Explora dados abertos sobre um tema específico.

    Args:
        tema: Tema de interesse (ex: saúde, educação, meio ambiente).
    """
    return (
        f"Explore os dados abertos disponíveis sobre '{tema}'.\n\n"
        "Passos:\n"
        f"1. Use buscar_conjuntos(texto='{tema}') para encontrar datasets\n"
        "2. Para cada dataset relevante, use detalhar_conjunto(conjunto_id=...) "
        "para ver detalhes\n"
        "3. Use buscar_recursos(conjunto_id=...) para encontrar os arquivos\n\n"
        "Apresente um relatório com:\n"
        "- Datasets mais relevantes\n"
        "- Organizações publicadoras\n"
        "- Formatos disponíveis\n"
        "- Frequência de atualização"
    )
