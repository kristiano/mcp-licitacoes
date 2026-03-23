"""Bacen feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_economica, comparar_indicadores
from .resources import catalogo_series, categorias_series, indicadores_chave
from .tools import (
    buscar_serie,
    calcular_variacao,
    comparar_series,
    consultar_serie,
    expectativas_focus,
    indicadores_atuais,
    metadados_serie,
    series_populares,
    ultimos_valores,
)

mcp = FastMCP("mcp-brasil-bacen")

# Tools
mcp.tool(consultar_serie)
mcp.tool(ultimos_valores)
mcp.tool(metadados_serie)
mcp.tool(series_populares)
mcp.tool(buscar_serie)
mcp.tool(indicadores_atuais)
mcp.tool(calcular_variacao)
mcp.tool(comparar_series)
mcp.tool(expectativas_focus)

# Resources (URIs without namespace prefix — mount adds "bacen/" automatically)
mcp.resource("data://catalogo", mime_type="application/json")(catalogo_series)
mcp.resource("data://categorias", mime_type="application/json")(categorias_series)
mcp.resource("data://indicadores-chave", mime_type="application/json")(indicadores_chave)

# Prompts
mcp.prompt(analise_economica)
mcp.prompt(comparar_indicadores)
