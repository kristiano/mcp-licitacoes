"""Feature Dados Abertos — catálogo de datasets do governo federal."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="dados_abertos",
    description=(
        "Portal Dados Abertos (dados.gov.br): catálogo de datasets abertos "
        "do governo federal, organizações publicadoras e recursos disponíveis."
    ),
    version="0.1.0",
    api_base="https://dados.gov.br/dados/api/publico",
    requires_auth=False,
    tags=["dados-abertos", "datasets", "governo", "transparencia"],
)
