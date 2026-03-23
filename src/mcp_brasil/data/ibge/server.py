"""IBGE feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import comparativo_regional, resumo_estado
from .resources import estados_brasileiros, niveis_territoriais, regioes_brasileiras
from .tools import (
    buscar_cnae,
    buscar_municipios,
    consultar_agregado,
    consultar_nome,
    listar_estados,
    listar_pesquisas,
    listar_regioes,
    obter_malha,
    ranking_nomes,
)

mcp = FastMCP("mcp-brasil-ibge")

# Tools
mcp.tool(listar_estados)
mcp.tool(buscar_municipios)
mcp.tool(listar_regioes)
mcp.tool(consultar_nome)
mcp.tool(ranking_nomes)
mcp.tool(consultar_agregado)
mcp.tool(listar_pesquisas)
mcp.tool(obter_malha)
mcp.tool(buscar_cnae)

# Resources (URIs without namespace prefix — mount adds "ibge/" automatically)
mcp.resource("data://estados", mime_type="application/json")(estados_brasileiros)
mcp.resource("data://regioes", mime_type="application/json")(regioes_brasileiras)
mcp.resource("data://niveis-territoriais", mime_type="application/json")(niveis_territoriais)

# Prompts
mcp.prompt(resumo_estado)
mcp.prompt(comparativo_regional)
