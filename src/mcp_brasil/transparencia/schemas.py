"""Pydantic models for Portal da Transparência API responses."""

from __future__ import annotations

from pydantic import BaseModel


class ContratoFornecedor(BaseModel):
    """Contrato federal por CPF/CNPJ do fornecedor."""

    id: int | None = None
    numero: str | None = None
    objeto: str | None = None
    valor_inicial: float | None = None
    valor_final: float | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    orgao: str | None = None
    fornecedor: str | None = None


class RecursoRecebido(BaseModel):
    """Recurso recebido (despesa) por favorecido."""

    ano: int | None = None
    mes: int | None = None
    valor: float | None = None
    favorecido_nome: str | None = None
    orgao_nome: str | None = None
    uf: str | None = None


class Servidor(BaseModel):
    """Servidor público federal."""

    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    tipo_servidor: str | None = None
    situacao: str | None = None
    orgao: str | None = None


class Licitacao(BaseModel):
    """Licitação federal."""

    id: int | None = None
    numero: str | None = None
    objeto: str | None = None
    modalidade: str | None = None
    situacao: str | None = None
    valor_estimado: float | None = None
    data_abertura: str | None = None
    orgao: str | None = None


class BolsaFamiliaMunicipio(BaseModel):
    """Dados do Novo Bolsa Família por município."""

    municipio: str | None = None
    uf: str | None = None
    quantidade: int | None = None
    valor: float | None = None
    data_referencia: str | None = None


class BolsaFamiliaSacado(BaseModel):
    """Dados do Novo Bolsa Família por NIS do sacado."""

    nis: str | None = None
    nome: str | None = None
    municipio: str | None = None
    uf: str | None = None
    valor: float | None = None


class Sancao(BaseModel):
    """Sanção de pessoa física ou jurídica."""

    fonte: str | None = None
    tipo: str | None = None
    nome: str | None = None
    cpf_cnpj: str | None = None
    orgao: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    fundamentacao: str | None = None


class Emenda(BaseModel):
    """Emenda parlamentar."""

    numero: str | None = None
    autor: str | None = None
    tipo: str | None = None
    localidade: str | None = None
    valor_empenhado: float | None = None
    valor_pago: float | None = None
    ano: int | None = None


class Viagem(BaseModel):
    """Viagem a serviço de servidor federal."""

    id: int | None = None
    cpf: str | None = None
    nome: str | None = None
    cargo: str | None = None
    orgao: str | None = None
    destino: str | None = None
    data_inicio: str | None = None
    data_fim: str | None = None
    valor_passagens: float | None = None
    valor_diarias: float | None = None
