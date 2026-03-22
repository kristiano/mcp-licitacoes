"""Tests for the transparencia tool functions.

Tools are tested by mocking client functions (never HTTP).
"""

from unittest.mock import AsyncMock, patch

import pytest

from mcp_brasil.transparencia import tools
from mcp_brasil.transparencia.schemas import (
    BolsaFamiliaMunicipio,
    BolsaFamiliaSacado,
    ContratoFornecedor,
    Emenda,
    Licitacao,
    RecursoRecebido,
    Sancao,
    Servidor,
    Viagem,
)

MODULE = "mcp_brasil.transparencia.client"


# ---------------------------------------------------------------------------
# buscar_contratos
# ---------------------------------------------------------------------------


class TestBuscarContratos:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            ContratoFornecedor(
                numero="CT-001",
                objeto="Serviço de TI",
                valor_final=120000.0,
                data_inicio="01/01/2024",
                data_fim="31/12/2024",
                orgao="MEC",
                fornecedor="Empresa XYZ",
            )
        ]
        with patch(f"{MODULE}.buscar_contratos", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_contratos("12345678000190")
        assert "CT-001" in result
        assert "R$ 120.000,00" in result
        assert "Empresa XYZ" not in result  # fornecedor is in header, not table
        assert "MEC" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_contratos", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_contratos("00000000000000")
        assert "Nenhum contrato" in result


# ---------------------------------------------------------------------------
# consultar_despesas
# ---------------------------------------------------------------------------


class TestConsultarDespesas:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            RecursoRecebido(
                ano=2024,
                mes=6,
                valor=50000.0,
                favorecido_nome="João Silva",
                orgao_nome="Min. Saúde",
                uf="DF",
            )
        ]
        with patch(f"{MODULE}.consultar_despesas", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.consultar_despesas("01/2024", "06/2024")
        assert "R$ 50.000,00" in result
        assert "João Silva" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.consultar_despesas", new_callable=AsyncMock, return_value=[]):
            result = await tools.consultar_despesas("01/2024", "06/2024")
        assert "Nenhuma despesa" in result


# ---------------------------------------------------------------------------
# buscar_servidores
# ---------------------------------------------------------------------------


class TestBuscarServidores:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Servidor(
                cpf="***123***",
                nome="Maria Santos",
                tipo_servidor="Civil",
                situacao="Ativo",
                orgao="INSS",
            )
        ]
        with patch(f"{MODULE}.buscar_servidores", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_servidores(cpf="12345678900")
        assert "Maria Santos" in result
        assert "INSS" in result

    @pytest.mark.asyncio
    async def test_no_params(self) -> None:
        result = await tools.buscar_servidores()
        assert "Informe CPF ou nome" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_servidores", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_servidores(nome="Fulano")
        assert "Nenhum servidor" in result


# ---------------------------------------------------------------------------
# buscar_licitacoes
# ---------------------------------------------------------------------------


class TestBuscarLicitacoes:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Licitacao(
                numero="PE-001",
                objeto="Compra de PCs",
                modalidade="Pregão",
                situacao="Aberta",
                valor_estimado=500000.0,
                data_abertura="15/03/2024",
                orgao="UFPI",
            )
        ]
        with patch(f"{MODULE}.buscar_licitacoes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_licitacoes(codigo_orgao="26246")
        assert "PE-001" in result
        assert "R$ 500.000,00" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_licitacoes", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_licitacoes()
        assert "Nenhuma licitação" in result


# ---------------------------------------------------------------------------
# consultar_bolsa_familia
# ---------------------------------------------------------------------------


class TestConsultarBolsaFamilia:
    @pytest.mark.asyncio
    async def test_no_params(self) -> None:
        result = await tools.consultar_bolsa_familia("202401")
        assert "Informe" in result

    @pytest.mark.asyncio
    async def test_by_municipio(self) -> None:
        mock_data = [
            BolsaFamiliaMunicipio(
                municipio="São Paulo",
                uf="SP",
                quantidade=100000,
                valor=25000000.0,
                data_referencia="202401",
            )
        ]
        with patch(
            f"{MODULE}.consultar_bolsa_familia_municipio",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_bolsa_familia("202401", codigo_ibge="3550308")
        assert "São Paulo" in result
        assert "R$ 25.000.000,00" in result

    @pytest.mark.asyncio
    async def test_by_nis(self) -> None:
        mock_data = [
            BolsaFamiliaSacado(
                nis="12345678901",
                nome="Ana Lima",
                municipio="Teresina",
                uf="PI",
                valor=600.0,
            )
        ]
        with patch(
            f"{MODULE}.consultar_bolsa_familia_nis",
            new_callable=AsyncMock,
            return_value=mock_data,
        ):
            result = await tools.consultar_bolsa_familia("202401", nis="12345678901")
        assert "Ana Lima" in result
        assert "R$ 600,00" in result

    @pytest.mark.asyncio
    async def test_nis_empty(self) -> None:
        with patch(
            f"{MODULE}.consultar_bolsa_familia_nis",
            new_callable=AsyncMock,
            return_value=[],
        ):
            result = await tools.consultar_bolsa_familia("202401", nis="99999999999")
        assert "Nenhum dado" in result


# ---------------------------------------------------------------------------
# buscar_sancoes
# ---------------------------------------------------------------------------


class TestBuscarSancoes:
    @pytest.mark.asyncio
    async def test_formats_results(self) -> None:
        mock_data = [
            Sancao(
                fonte="CEIS",
                tipo="Inidoneidade",
                nome="Empresa Má",
                cpf_cnpj="12.345.678/0001-90",
                orgao="CGU",
                data_inicio="01/01/2023",
                data_fim="01/01/2028",
                fundamentacao="Lei 8666/93",
            )
        ]
        with patch(f"{MODULE}.buscar_sancoes", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_sancoes("12345678000190")
        assert "Empresa Má" in result
        assert "CEIS" in result
        assert "CGU" in result
        assert "Lei 8666/93" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_sancoes", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_sancoes("00000000000000")
        assert "Nenhuma sanção" in result


# ---------------------------------------------------------------------------
# buscar_emendas
# ---------------------------------------------------------------------------


class TestBuscarEmendas:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Emenda(
                numero="EMD-001",
                autor="Dep. Fulano",
                tipo="Individual",
                localidade="Teresina",
                valor_empenhado=1000000.0,
                valor_pago=500000.0,
                ano=2024,
            )
        ]
        with patch(f"{MODULE}.buscar_emendas", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.buscar_emendas(ano=2024)
        assert "EMD-001" in result
        assert "Dep. Fulano" in result
        assert "R$ 1.000.000,00" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.buscar_emendas", new_callable=AsyncMock, return_value=[]):
            result = await tools.buscar_emendas()
        assert "Nenhuma emenda" in result


# ---------------------------------------------------------------------------
# consultar_viagens
# ---------------------------------------------------------------------------


class TestConsultarViagens:
    @pytest.mark.asyncio
    async def test_formats_table(self) -> None:
        mock_data = [
            Viagem(
                nome="Pedro Almeida",
                cargo="Analista",
                orgao="MRE",
                destino="Brasília/DF",
                data_inicio="01/03/2024",
                data_fim="05/03/2024",
                valor_passagens=1500.0,
                valor_diarias=2000.0,
            )
        ]
        with patch(f"{MODULE}.consultar_viagens", new_callable=AsyncMock, return_value=mock_data):
            result = await tools.consultar_viagens("12345678900")
        assert "Pedro Almeida" in result
        assert "R$ 2.000,00" in result
        assert "Brasília/DF" in result

    @pytest.mark.asyncio
    async def test_empty(self) -> None:
        with patch(f"{MODULE}.consultar_viagens", new_callable=AsyncMock, return_value=[]):
            result = await tools.consultar_viagens("00000000000")
        assert "Nenhuma viagem" in result
