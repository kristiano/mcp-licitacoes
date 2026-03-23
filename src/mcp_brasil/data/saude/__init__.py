"""Feature Saúde — dados de estabelecimentos de saúde via CNES/DataSUS."""

from mcp_brasil._shared.feature import FeatureMeta

FEATURE_META = FeatureMeta(
    name="saude",
    description=(
        "CNES/DataSUS: estabelecimentos de saúde, profissionais, "
        "tipos de estabelecimento e leitos hospitalares."
    ),
    version="0.1.0",
    api_base="https://apidadosabertos.saude.gov.br/cnes",
    requires_auth=False,
    tags=["saude", "sus", "cnes", "hospitais", "leitos"],
)
