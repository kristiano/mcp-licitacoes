"""HTTP client for the Portal da Transparência API.

Ported and expanded from mcp-dadosbr/lib/tools/government.ts
(executeTransparencia + executeCeisCnep).

All functions return typed Pydantic models. No LLM formatting here (ADR-001).
Auth is injected via the ``chave-api-dados`` header using ``http_get()``.

Endpoints:
    - /contratos/cpf-cnpj             → buscar_contratos
    - /despesas/recursos-recebidos     → consultar_despesas
    - /servidores                      → buscar_servidores
    - /licitacoes                      → buscar_licitacoes
    - /novo-bolsa-familia-por-municipio → consultar_bolsa_familia_municipio
    - /novo-bolsa-familia-sacado-por-nis → consultar_bolsa_familia_nis
    - /ceis, /cnep, /cepim, /ceaf      → buscar_sancoes
    - /emendas                         → buscar_emendas
    - /viagens-por-cpf                 → consultar_viagens
"""

from __future__ import annotations

import asyncio
import logging
import os
import re
from typing import Any

from mcp_brasil._shared.http_client import http_get
from mcp_brasil.exceptions import AuthError

from .constants import (
    AUTH_ENV_VAR,
    AUTH_HEADER_NAME,
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
from .schemas import (
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

logger = logging.getLogger(__name__)


def _get_api_key() -> str:
    """Return the API key or raise AuthError."""
    key = os.environ.get(AUTH_ENV_VAR, "")
    if not key:
        raise AuthError(
            f"Variável de ambiente {AUTH_ENV_VAR} não configurada. "
            "Cadastre-se em portaldatransparencia.gov.br/api-de-dados/cadastrar-email"
        )
    return key


def _auth_headers() -> dict[str, str]:
    """Build auth headers for the API."""
    return {AUTH_HEADER_NAME: _get_api_key()}


def _clean_cpf_cnpj(valor: str) -> str:
    """Remove non-digit characters from CPF/CNPJ."""
    return re.sub(r"\D", "", valor)


async def _get(url: str, params: dict[str, Any] | None = None) -> Any:
    """Make an authenticated GET request to the Portal da Transparência API."""
    return await http_get(url, params=params, headers=_auth_headers())


# --- Parsing helpers --------------------------------------------------------


def _parse_contrato(raw: dict[str, Any]) -> ContratoFornecedor:
    """Parse a raw contract JSON into a ContratoFornecedor model."""
    fornecedor = raw.get("fornecedor") or {}
    orgao = raw.get("unidadeGestora") or raw.get("orgaoVinculado") or {}
    return ContratoFornecedor(
        id=raw.get("id"),
        numero=raw.get("numero"),
        objeto=raw.get("objeto"),
        valor_inicial=raw.get("valorInicial"),
        valor_final=raw.get("valorFinal"),
        data_inicio=raw.get("dataInicioVigencia"),
        data_fim=raw.get("dataFimVigencia"),
        orgao=orgao.get("nome") or orgao.get("descricao"),
        fornecedor=fornecedor.get("nome") or fornecedor.get("razaoSocialReceita"),
    )


def _parse_recurso(raw: dict[str, Any]) -> RecursoRecebido:
    """Parse a raw expense/resource JSON."""
    return RecursoRecebido(
        ano=raw.get("ano"),
        mes=raw.get("mes"),
        valor=raw.get("valor"),
        favorecido_nome=raw.get("nomeFavorecido"),
        orgao_nome=raw.get("nomeOrgao"),
        uf=raw.get("uf"),
    )


def _parse_servidor(raw: dict[str, Any]) -> Servidor:
    """Parse a raw server/public servant JSON."""
    orgao = raw.get("orgaoServidorExercicio") or raw.get("orgaoServidorLotacao") or {}
    return Servidor(
        id=raw.get("id"),
        cpf=raw.get("cpf"),
        nome=raw.get("nome"),
        tipo_servidor=raw.get("tipoServidor"),
        situacao=raw.get("situacao"),
        orgao=orgao.get("nome") or orgao.get("descricao"),
    )


def _parse_licitacao(raw: dict[str, Any]) -> Licitacao:
    """Parse a raw procurement/bid JSON."""
    orgao = raw.get("unidadeGestora") or raw.get("orgao") or {}
    return Licitacao(
        id=raw.get("id"),
        numero=raw.get("numero"),
        objeto=raw.get("objeto"),
        modalidade=raw.get("modalidadeLicitacao") or raw.get("modalidade"),
        situacao=raw.get("situacao"),
        valor_estimado=raw.get("valorEstimado"),
        data_abertura=raw.get("dataAbertura") or raw.get("dataResultadoCompra"),
        orgao=orgao.get("nome") or orgao.get("descricao"),
    )


def _parse_bolsa_municipio(raw: dict[str, Any]) -> BolsaFamiliaMunicipio:
    """Parse Bolsa Família municipality data."""
    municipio = raw.get("municipio") or {}
    return BolsaFamiliaMunicipio(
        municipio=municipio.get("nomeIBGE") or raw.get("municipio"),
        uf=municipio.get("uf", {}).get("sigla") if isinstance(municipio.get("uf"), dict) else None,
        quantidade=raw.get("quantidadeBeneficiados"),
        valor=raw.get("valor"),
        data_referencia=raw.get("dataReferencia"),
    )


def _parse_bolsa_sacado(raw: dict[str, Any]) -> BolsaFamiliaSacado:
    """Parse Bolsa Família NIS beneficiary data."""
    municipio = raw.get("municipio") or {}
    return BolsaFamiliaSacado(
        nis=raw.get("nis"),
        nome=raw.get("nome"),
        municipio=municipio.get("nomeIBGE") if isinstance(municipio, dict) else None,
        uf=municipio.get("uf", {}).get("sigla")
        if isinstance(municipio, dict) and isinstance(municipio.get("uf"), dict)
        else None,
        valor=raw.get("valor"),
    )


def _parse_sancao(raw: dict[str, Any], fonte: str) -> Sancao:
    """Parse a sanction record from any of the 4 databases."""
    sancionado = raw.get("sancionado") or raw.get("pessoaSancionada") or {}
    orgao = raw.get("orgaoSancionador") or {}
    return Sancao(
        fonte=fonte,
        tipo=raw.get("tipoSancao") or raw.get("tipoPenalidade"),
        nome=sancionado.get("nome") or sancionado.get("razaoSocialReceita"),
        cpf_cnpj=sancionado.get("codigoFormatado") or sancionado.get("cnpjFormatado"),
        orgao=orgao.get("nome"),
        data_inicio=raw.get("dataInicioSancao") or raw.get("dataPublicacao"),
        data_fim=raw.get("dataFimSancao") or raw.get("dataFinalSancao"),
        fundamentacao=raw.get("fundamentacaoLegal") or raw.get("fundamentacao"),
    )


def _parse_emenda(raw: dict[str, Any]) -> Emenda:
    """Parse a parliamentary amendment record."""
    autor = raw.get("autor") or {}
    localidade = raw.get("localidadeDoGasto") or {}
    return Emenda(
        numero=raw.get("numero") or raw.get("codigoEmenda"),
        autor=autor.get("nome") if isinstance(autor, dict) else str(autor) if autor else None,
        tipo=raw.get("tipoEmenda"),
        localidade=localidade.get("nome")
        if isinstance(localidade, dict)
        else str(localidade)
        if localidade
        else None,
        valor_empenhado=raw.get("valorEmpenhado"),
        valor_pago=raw.get("valorPago"),
        ano=raw.get("ano"),
    )


def _parse_viagem(raw: dict[str, Any]) -> Viagem:
    """Parse a federal travel record."""
    return Viagem(
        id=raw.get("id"),
        cpf=raw.get("cpf"),
        nome=raw.get("nome") or raw.get("nomeProposto"),
        cargo=raw.get("cargo") or raw.get("funcao"),
        orgao=raw.get("nomeOrgao"),
        destino=raw.get("destinos") or raw.get("destino"),
        data_inicio=raw.get("dataInicio") or raw.get("dataInicioAfastamento"),
        data_fim=raw.get("dataFim") or raw.get("dataFimAfastamento"),
        valor_passagens=raw.get("valorPassagens"),
        valor_diarias=raw.get("valorDiarias"),
    )


# --- Public API functions ---------------------------------------------------


async def buscar_contratos(cpf_cnpj: str, pagina: int = 1) -> list[ContratoFornecedor]:
    """Busca contratos federais por CPF/CNPJ do fornecedor.

    Args:
        cpf_cnpj: CPF ou CNPJ do fornecedor (aceita formatado ou só dígitos).
        pagina: Número da página de resultados.
    """
    params = {"cpfCnpj": _clean_cpf_cnpj(cpf_cnpj), "pagina": pagina}
    data = await _get(CONTRATOS_URL, params)
    if isinstance(data, list):
        return [_parse_contrato(item) for item in data]
    return []


async def consultar_despesas(
    mes_ano_inicio: str,
    mes_ano_fim: str,
    codigo_favorecido: str | None = None,
    pagina: int = 1,
) -> list[RecursoRecebido]:
    """Consulta despesas/recursos recebidos por favorecido.

    Args:
        mes_ano_inicio: Mês/ano início no formato MM/AAAA.
        mes_ano_fim: Mês/ano fim no formato MM/AAAA.
        codigo_favorecido: CPF ou CNPJ do favorecido.
        pagina: Número da página.
    """
    params: dict[str, Any] = {
        "mesAnoInicio": mes_ano_inicio,
        "mesAnoFim": mes_ano_fim,
        "pagina": pagina,
    }
    if codigo_favorecido:
        params["codigoFavorecido"] = _clean_cpf_cnpj(codigo_favorecido)
    data = await _get(DESPESAS_URL, params)
    if isinstance(data, list):
        return [_parse_recurso(item) for item in data]
    return []


async def buscar_servidores(
    cpf: str | None = None,
    nome: str | None = None,
    pagina: int = 1,
) -> list[Servidor]:
    """Busca servidores públicos federais por CPF ou nome.

    Args:
        cpf: CPF do servidor (opcional se nome fornecido).
        nome: Nome do servidor (opcional se CPF fornecido).
        pagina: Número da página.
    """
    params: dict[str, Any] = {"pagina": pagina}
    if cpf:
        params["cpf"] = _clean_cpf_cnpj(cpf)
    elif nome:
        params["nome"] = nome
    data = await _get(SERVIDORES_URL, params)
    if isinstance(data, list):
        return [_parse_servidor(item) for item in data]
    return []


async def buscar_licitacoes(
    codigo_orgao: str | None = None,
    data_inicial: str | None = None,
    data_final: str | None = None,
    pagina: int = 1,
) -> list[Licitacao]:
    """Busca licitações federais.

    Args:
        codigo_orgao: Código do órgão (SIAFI).
        data_inicial: Data inicial no formato DD/MM/AAAA.
        data_final: Data final no formato DD/MM/AAAA.
        pagina: Número da página.
    """
    params: dict[str, Any] = {"pagina": pagina}
    if codigo_orgao:
        params["codigoOrgao"] = codigo_orgao
    if data_inicial:
        params["dataInicial"] = data_inicial
    if data_final:
        params["dataFinal"] = data_final
    data = await _get(LICITACOES_URL, params)
    if isinstance(data, list):
        return [_parse_licitacao(item) for item in data]
    return []


async def consultar_bolsa_familia_municipio(
    mes_ano: str,
    codigo_ibge: str,
    pagina: int = 1,
) -> list[BolsaFamiliaMunicipio]:
    """Consulta dados do Novo Bolsa Família por município.

    Args:
        mes_ano: Mês/ano de referência no formato AAAAMM.
        codigo_ibge: Código IBGE do município.
        pagina: Número da página.
    """
    params: dict[str, Any] = {
        "mesAno": mes_ano,
        "codigoIbge": codigo_ibge,
        "pagina": pagina,
    }
    data = await _get(BOLSA_FAMILIA_MUNICIPIO_URL, params)
    if isinstance(data, list):
        return [_parse_bolsa_municipio(item) for item in data]
    return []


async def consultar_bolsa_familia_nis(
    mes_ano: str,
    nis: str,
    pagina: int = 1,
) -> list[BolsaFamiliaSacado]:
    """Consulta dados do Novo Bolsa Família por NIS do sacado.

    Args:
        mes_ano: Mês/ano de referência no formato AAAAMM.
        nis: Número de Identificação Social do beneficiário.
        pagina: Número da página.
    """
    params: dict[str, Any] = {
        "mesAno": mes_ano,
        "nis": nis,
        "pagina": pagina,
    }
    data = await _get(BOLSA_FAMILIA_NIS_URL, params)
    if isinstance(data, list):
        return [_parse_bolsa_sacado(item) for item in data]
    return []


async def buscar_sancoes(
    consulta: str,
    bases: list[str] | None = None,
    pagina: int = 1,
) -> list[Sancao]:
    """Busca sanções em paralelo nas bases CEIS, CNEP, CEPIM e CEAF.

    Tenta primeiro por CPF/CNPJ; se falhar, tenta por nome.

    Args:
        consulta: CPF, CNPJ ou nome da pessoa/empresa.
        bases: Lista de bases a consultar (default: todas).
        pagina: Número da página.
    """
    bases_alvo = bases or list(SANCOES_DATABASES.keys())
    headers = _auth_headers()

    async def _consultar_base(base_key: str) -> list[Sancao]:
        db = SANCOES_DATABASES.get(base_key)
        if not db:
            return []

        url = db["url"]
        is_digits = consulta.strip().replace(".", "").replace("-", "").replace("/", "").isdigit()

        if is_digits:
            param_key = db["param_cpf_cnpj"]
            params: dict[str, Any] = {param_key: _clean_cpf_cnpj(consulta), "pagina": pagina}
        else:
            param_key = db["param_nome"]
            params = {param_key: consulta, "pagina": pagina}

        try:
            data = await http_get(url, params=params, headers=headers)
            if isinstance(data, list):
                return [_parse_sancao(item, db["nome"]) for item in data]
        except Exception:
            logger.warning("Falha ao consultar base %s para '%s'", base_key, consulta)
        return []

    results = await asyncio.gather(*[_consultar_base(b) for b in bases_alvo])
    return [sancao for sublist in results for sancao in sublist]


async def buscar_emendas(
    ano: int | None = None,
    nome_autor: str | None = None,
    pagina: int = 1,
) -> list[Emenda]:
    """Busca emendas parlamentares.

    Args:
        ano: Ano da emenda.
        nome_autor: Nome do autor da emenda.
        pagina: Número da página.
    """
    params: dict[str, Any] = {"pagina": pagina}
    if ano:
        params["ano"] = ano
    if nome_autor:
        params["nomeAutor"] = nome_autor
    data = await _get(EMENDAS_URL, params)
    if isinstance(data, list):
        return [_parse_emenda(item) for item in data]
    return []


async def consultar_viagens(cpf: str, pagina: int = 1) -> list[Viagem]:
    """Consulta viagens a serviço por CPF do servidor.

    Args:
        cpf: CPF do servidor.
        pagina: Número da página.
    """
    params: dict[str, Any] = {"cpf": _clean_cpf_cnpj(cpf), "pagina": pagina}
    data = await _get(VIAGENS_URL, params)
    if isinstance(data, list):
        return [_parse_viagem(item) for item in data]
    return []
