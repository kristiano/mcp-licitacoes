"""Pydantic schemas for the Dados Abertos feature."""

from __future__ import annotations

from pydantic import BaseModel


class ConjuntoDados(BaseModel):
    """Dataset do Portal Dados Abertos."""

    id: str | None = None
    titulo: str | None = None
    descricao: str | None = None
    organizacao_nome: str | None = None
    temas: list[str] = []
    tags: list[str] = []
    data_criacao: str | None = None
    data_atualizacao: str | None = None


class ConjuntoResultado(BaseModel):
    """Resultado paginado de busca de conjuntos."""

    total: int = 0
    conjuntos: list[ConjuntoDados] = []


class Organizacao(BaseModel):
    """Organização publicadora de dados."""

    id: str | None = None
    nome: str | None = None
    descricao: str | None = None
    total_conjuntos: int | None = None


class OrganizacaoResultado(BaseModel):
    """Resultado paginado de organizações."""

    total: int = 0
    organizacoes: list[Organizacao] = []


class RecursoDados(BaseModel):
    """Recurso (arquivo/API) de um dataset."""

    id: str | None = None
    titulo: str | None = None
    link: str | None = None
    formato: str | None = None
    descricao: str | None = None


class RecursoResultado(BaseModel):
    """Resultado paginado de recursos."""

    total: int = 0
    recursos: list[RecursoDados] = []
