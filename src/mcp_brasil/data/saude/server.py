"""Saúde feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_rede_saude
from .resources import codigos_uf_cnes
from .tools import (
    buscar_estabelecimentos,
    buscar_profissionais,
    consultar_leitos,
    listar_tipos_estabelecimento,
)

mcp = FastMCP("mcp-brasil-saude")

# Tools (4)
mcp.tool(buscar_estabelecimentos)
mcp.tool(buscar_profissionais)
mcp.tool(listar_tipos_estabelecimento)
mcp.tool(consultar_leitos)

# Resources (URIs without namespace prefix — mount adds "saude/" automatically)
mcp.resource("data://codigos-uf", mime_type="application/json")(codigos_uf_cnes)

# Prompts
mcp.prompt(analise_rede_saude)
