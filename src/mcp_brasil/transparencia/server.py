"""Transparência feature server — registers tools on a FastMCP instance.

This file only registers tools. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .tools import (
    buscar_contratos,
    buscar_emendas,
    buscar_licitacoes,
    buscar_sancoes,
    buscar_servidores,
    consultar_bolsa_familia,
    consultar_despesas,
    consultar_viagens,
)

mcp = FastMCP("mcp-brasil-transparencia")

mcp.tool(buscar_contratos)
mcp.tool(consultar_despesas)
mcp.tool(buscar_servidores)
mcp.tool(buscar_licitacoes)
mcp.tool(consultar_bolsa_familia)
mcp.tool(buscar_sancoes)
mcp.tool(buscar_emendas)
mcp.tool(consultar_viagens)
