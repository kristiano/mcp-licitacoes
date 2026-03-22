"""Feature Transparência — Portal da Transparência do Governo Federal."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="transparencia",
    description="Portal da Transparência: contratos, despesas, servidores, licitações, sanções",
    version="0.1.0",
    api_base="https://api.portaldatransparencia.gov.br/api-de-dados",
    requires_auth=True,
    auth_env_var="TRANSPARENCIA_API_KEY",
    tags=["governo", "contratos", "despesas", "servidores", "licitações", "sanções"],
)
