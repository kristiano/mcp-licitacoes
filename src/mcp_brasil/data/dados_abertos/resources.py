"""Static reference data for the Dados Abertos feature."""

from __future__ import annotations

import json


def formatos_disponiveis() -> str:
    """Formatos de arquivo comuns no Portal Dados Abertos."""
    data = [
        {"formato": "CSV", "descricao": "Valores separados por vírgula"},
        {"formato": "JSON", "descricao": "JavaScript Object Notation"},
        {"formato": "XML", "descricao": "Extensible Markup Language"},
        {"formato": "XLS/XLSX", "descricao": "Planilha Microsoft Excel"},
        {"formato": "ODS", "descricao": "Open Document Spreadsheet"},
        {"formato": "PDF", "descricao": "Documento portátil"},
        {"formato": "API", "descricao": "Interface programática"},
    ]
    return json.dumps(data, ensure_ascii=False, indent=2)
