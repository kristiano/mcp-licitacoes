"""Pydantic schemas for the Bacen feature.

Ported from bcb-br-mcp/src/tools.ts interfaces SerieValor, SerieMetadados.
"""

from __future__ import annotations

from pydantic import BaseModel


class SerieValor(BaseModel):
    """A single data point from a BCB time series."""

    data: str
    valor: float


class SerieMetadados(BaseModel):
    """Metadata for a BCB time series."""

    codigo: int
    nome: str
    unidade: str = "Não informada"
    periodicidade: str = "Não informada"
    fonte: str = "Banco Central do Brasil"
    especial: bool = False
