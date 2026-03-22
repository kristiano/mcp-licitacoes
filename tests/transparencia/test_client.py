"""Tests for the transparencia HTTP client."""

from unittest.mock import patch

import httpx
import pytest
import respx

from mcp_brasil.exceptions import AuthError
from mcp_brasil.transparencia import client
from mcp_brasil.transparencia.constants import (
    AUTH_ENV_VAR,
    BOLSA_FAMILIA_MUNICIPIO_URL,
    BOLSA_FAMILIA_NIS_URL,
    CONTRATOS_URL,
    DESPESAS_URL,
    EMENDAS_URL,
    LICITACOES_URL,
    SANCOES_DATABASES,
    SERVIDORES_URL,
    VIAGENS_URL,
)


@pytest.fixture(autouse=True)
def _set_api_key(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set a fake API key for all tests."""
    monkeypatch.setenv(AUTH_ENV_VAR, "test-api-key-123")


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------


class TestAuth:
    def test_get_api_key_success(self) -> None:
        key = client._get_api_key()
        assert key == "test-api-key-123"

    def test_get_api_key_missing(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.delenv(AUTH_ENV_VAR)
        with pytest.raises(AuthError, match=AUTH_ENV_VAR):
            client._get_api_key()

    def test_auth_headers(self) -> None:
        headers = client._auth_headers()
        assert headers == {"chave-api-dados": "test-api-key-123"}


class TestCleanCpfCnpj:
    def test_digits_only(self) -> None:
        assert client._clean_cpf_cnpj("12345678000190") == "12345678000190"

    def test_formatted_cnpj(self) -> None:
        assert client._clean_cpf_cnpj("12.345.678/0001-90") == "12345678000190"

    def test_formatted_cpf(self) -> None:
        assert client._clean_cpf_cnpj("123.456.789-09") == "12345678909"


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_contracts(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 1,
                        "numero": "CT-001",
                        "objeto": "Serviço de TI",
                        "valorInicial": 100000.0,
                        "valorFinal": 120000.0,
                        "dataInicioVigencia": "01/01/2024",
                        "dataFimVigencia": "31/12/2024",
                        "unidadeGestora": {"nome": "MEC"},
                        "fornecedor": {"nome": "Empresa XYZ"},
                    }
                ],
            )
        )
        result = await client.buscar_contratos("12345678000190")
        assert len(result) == 1
        assert result[0].numero == "CT-001"
        assert result[0].valor_final == 120000.0
        assert result[0].orgao == "MEC"
        assert result[0].fornecedor == "Empresa XYZ"

    @pytest.mark.asyncio
    @respx.mock
    async def test_empty_response(self) -> None:
        respx.get(CONTRATOS_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_contratos("00000000000000")
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_non_list_response(self) -> None:
        respx.get(CONTRATOS_URL).mock(
            return_value=httpx.Response(200, json={"message": "not found"})
        )
        result = await client.buscar_contratos("00000000000000")
        assert result == []


# ---------------------------------------------------------------------------
# consultar_despesas
# ---------------------------------------------------------------------------


class TestConsultarDespesas:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_expenses(self) -> None:
        respx.get(DESPESAS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "ano": 2024,
                        "mes": 6,
                        "valor": 50000.0,
                        "nomeFavorecido": "João Silva",
                        "nomeOrgao": "Ministério da Saúde",
                        "uf": "DF",
                    }
                ],
            )
        )
        result = await client.consultar_despesas("01/2024", "06/2024")
        assert len(result) == 1
        assert result[0].valor == 50000.0
        assert result[0].favorecido_nome == "João Silva"

    @pytest.mark.asyncio
    @respx.mock
    async def test_with_favorecido(self) -> None:
        route = respx.get(DESPESAS_URL).mock(return_value=httpx.Response(200, json=[]))
        await client.consultar_despesas("01/2024", "06/2024", "12345678000190")
        assert "codigoFavorecido" in str(route.calls[0].request.url)


# ---------------------------------------------------------------------------
# buscar_servidores
# ---------------------------------------------------------------------------


class TestBuscarServidores:
    @pytest.mark.asyncio
    @respx.mock
    async def test_by_cpf(self) -> None:
        respx.get(SERVIDORES_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 42,
                        "cpf": "***123456**",
                        "nome": "Maria Santos",
                        "tipoServidor": "Civil",
                        "situacao": "Ativo",
                        "orgaoServidorExercicio": {"nome": "INSS"},
                    }
                ],
            )
        )
        result = await client.buscar_servidores(cpf="12345678900")
        assert len(result) == 1
        assert result[0].nome == "Maria Santos"
        assert result[0].orgao == "INSS"

    @pytest.mark.asyncio
    @respx.mock
    async def test_by_nome(self) -> None:
        respx.get(SERVIDORES_URL).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_servidores(nome="Carlos")
        assert result == []


# ---------------------------------------------------------------------------
# buscar_licitacoes
# ---------------------------------------------------------------------------


class TestBuscarLicitacoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_bids(self) -> None:
        respx.get(LICITACOES_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 10,
                        "numero": "PE-2024/001",
                        "objeto": "Aquisição de computadores",
                        "modalidadeLicitacao": "Pregão Eletrônico",
                        "situacao": "Aberta",
                        "valorEstimado": 500000.0,
                        "dataAbertura": "15/03/2024",
                        "unidadeGestora": {"nome": "UFPI"},
                    }
                ],
            )
        )
        result = await client.buscar_licitacoes(codigo_orgao="26246")
        assert len(result) == 1
        assert result[0].modalidade == "Pregão Eletrônico"
        assert result[0].orgao == "UFPI"


# ---------------------------------------------------------------------------
# consultar_bolsa_familia
# ---------------------------------------------------------------------------


class TestBolsaFamilia:
    @pytest.mark.asyncio
    @respx.mock
    async def test_municipio(self) -> None:
        respx.get(BOLSA_FAMILIA_MUNICIPIO_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "municipio": {"nomeIBGE": "São Paulo", "uf": {"sigla": "SP"}},
                        "quantidadeBeneficiados": 100000,
                        "valor": 25000000.0,
                        "dataReferencia": "202401",
                    }
                ],
            )
        )
        result = await client.consultar_bolsa_familia_municipio("202401", "3550308")
        assert len(result) == 1
        assert result[0].municipio == "São Paulo"
        assert result[0].uf == "SP"
        assert result[0].quantidade == 100000

    @pytest.mark.asyncio
    @respx.mock
    async def test_nis(self) -> None:
        respx.get(BOLSA_FAMILIA_NIS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "nis": "12345678901",
                        "nome": "Ana Lima",
                        "municipio": {"nomeIBGE": "Teresina", "uf": {"sigla": "PI"}},
                        "valor": 600.0,
                    }
                ],
            )
        )
        result = await client.consultar_bolsa_familia_nis("202401", "12345678901")
        assert len(result) == 1
        assert result[0].nome == "Ana Lima"
        assert result[0].valor == 600.0


# ---------------------------------------------------------------------------
# buscar_sancoes
# ---------------------------------------------------------------------------


class TestBuscarSancoes:
    @pytest.mark.asyncio
    @respx.mock
    async def test_single_base_by_cnpj(self) -> None:
        db = SANCOES_DATABASES["ceis"]
        respx.get(db["url"]).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "sancionado": {
                            "nome": "Empresa Sancionada",
                            "codigoFormatado": "12.345.678/0001-90",
                        },
                        "orgaoSancionador": {"nome": "CGU"},
                        "tipoSancao": "Inidoneidade",
                        "dataInicioSancao": "01/01/2023",
                        "dataFimSancao": "01/01/2028",
                        "fundamentacaoLegal": "Lei 8666/93",
                    }
                ],
            )
        )
        result = await client.buscar_sancoes("12345678000190", bases=["ceis"])
        assert len(result) == 1
        assert result[0].nome == "Empresa Sancionada"
        assert result[0].fonte == SANCOES_DATABASES["ceis"]["nome"]

    @pytest.mark.asyncio
    @respx.mock
    async def test_all_bases_parallel(self) -> None:
        for db in SANCOES_DATABASES.values():
            respx.get(db["url"]).mock(return_value=httpx.Response(200, json=[]))
        result = await client.buscar_sancoes("Empresa Teste")
        assert result == []

    @pytest.mark.asyncio
    @respx.mock
    async def test_partial_failure(self) -> None:
        """One base fails, others succeed — no exception raised."""
        ceis = SANCOES_DATABASES["ceis"]
        cnep = SANCOES_DATABASES["cnep"]
        cepim = SANCOES_DATABASES["cepim"]
        ceaf = SANCOES_DATABASES["ceaf"]

        respx.get(ceis["url"]).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "sancionado": {"nome": "Teste"},
                        "orgaoSancionador": {},
                    }
                ],
            )
        )
        respx.get(cnep["url"]).mock(return_value=httpx.Response(500, text="Error"))
        respx.get(cepim["url"]).mock(return_value=httpx.Response(200, json=[]))
        respx.get(ceaf["url"]).mock(return_value=httpx.Response(200, json=[]))

        with patch("mcp_brasil._shared.http_client.asyncio.sleep"):
            result = await client.buscar_sancoes("12345678000190", pagina=1)
        assert len(result) == 1


# ---------------------------------------------------------------------------
# buscar_emendas
# ---------------------------------------------------------------------------


class TestBuscarEmendas:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_amendments(self) -> None:
        respx.get(EMENDAS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "codigoEmenda": "EMD-001",
                        "autor": {"nome": "Dep. Fulano"},
                        "tipoEmenda": "Individual",
                        "localidadeDoGasto": {"nome": "Teresina"},
                        "valorEmpenhado": 1000000.0,
                        "valorPago": 500000.0,
                        "ano": 2024,
                    }
                ],
            )
        )
        result = await client.buscar_emendas(ano=2024)
        assert len(result) == 1
        assert result[0].autor == "Dep. Fulano"
        assert result[0].valor_empenhado == 1000000.0


# ---------------------------------------------------------------------------
# consultar_viagens
# ---------------------------------------------------------------------------


class TestConsultarViagens:
    @pytest.mark.asyncio
    @respx.mock
    async def test_returns_parsed_trips(self) -> None:
        respx.get(VIAGENS_URL).mock(
            return_value=httpx.Response(
                200,
                json=[
                    {
                        "id": 99,
                        "cpf": "***123456**",
                        "nome": "Pedro Almeida",
                        "cargo": "Analista",
                        "nomeOrgao": "MRE",
                        "destinos": "Brasília/DF",
                        "dataInicio": "01/03/2024",
                        "dataFim": "05/03/2024",
                        "valorPassagens": 1500.0,
                        "valorDiarias": 2000.0,
                    }
                ],
            )
        )
        result = await client.consultar_viagens("12345678900")
        assert len(result) == 1
        assert result[0].nome == "Pedro Almeida"
        assert result[0].valor_diarias == 2000.0
        assert result[0].destino == "Brasília/DF"
