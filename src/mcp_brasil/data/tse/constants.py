"""Constants for the TSE (Tribunal Superior Eleitoral) feature."""

# API base URL
TSE_API_BASE = "https://divulgacandcontas.tse.jus.br/divulga/rest/v1"

# Endpoints
ELEICAO_URL = f"{TSE_API_BASE}/eleicao"
CANDIDATURA_URL = f"{TSE_API_BASE}/candidatura"
PRESTADOR_URL = f"{TSE_API_BASE}/prestador"

# Default pagination
DEFAULT_PAGE_SIZE = 50

# Códigos de cargos eleitorais
CARGOS_ELEITORAIS: list[dict[str, str | int]] = [
    {"codigo": 1, "nome": "Presidente", "tipo": "Federal"},
    {"codigo": 2, "nome": "Vice-Presidente", "tipo": "Federal"},
    {"codigo": 3, "nome": "Governador", "tipo": "Estadual"},
    {"codigo": 4, "nome": "Vice-Governador", "tipo": "Estadual"},
    {"codigo": 5, "nome": "Senador", "tipo": "Federal"},
    {"codigo": 6, "nome": "Deputado Federal", "tipo": "Federal"},
    {"codigo": 7, "nome": "Deputado Estadual", "tipo": "Estadual"},
    {"codigo": 8, "nome": "Deputado Distrital", "tipo": "Distrital"},
    {"codigo": 9, "nome": "1º Suplente Senador", "tipo": "Federal"},
    {"codigo": 10, "nome": "2º Suplente Senador", "tipo": "Federal"},
    {"codigo": 11, "nome": "Prefeito", "tipo": "Municipal"},
    {"codigo": 12, "nome": "Vice-Prefeito", "tipo": "Municipal"},
    {"codigo": 13, "nome": "Vereador", "tipo": "Municipal"},
]
