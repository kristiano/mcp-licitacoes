"""Compras feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import investigar_fornecedor
from .resources import modalidades_licitacao
from .tools import (
    buscar_atas,
    buscar_contratacoes,
    buscar_contratos,
    buscar_itens,
    consultar_fornecedor,
    consultar_orgao,
)

mcp = FastMCP("mcp-brasil-compras")

# Tools
mcp.tool(buscar_contratacoes)
mcp.tool(buscar_contratos)
mcp.tool(buscar_atas)
mcp.tool(consultar_fornecedor)
mcp.tool(buscar_itens)
mcp.tool(consultar_orgao)

# Resources
mcp.resource("data://modalidades", mime_type="application/json")(modalidades_licitacao)

# Prompts
mcp.prompt(investigar_fornecedor)
