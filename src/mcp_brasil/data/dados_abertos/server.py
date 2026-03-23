"""Dados Abertos feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import explorar_dados
from .resources import formatos_disponiveis
from .tools import buscar_conjuntos, buscar_recursos, detalhar_conjunto, listar_organizacoes

mcp = FastMCP("mcp-brasil-dados-abertos")

# Tools
mcp.tool(buscar_conjuntos)
mcp.tool(detalhar_conjunto)
mcp.tool(listar_organizacoes)
mcp.tool(buscar_recursos)

# Resources
mcp.resource("data://formatos", mime_type="application/json")(formatos_disponiveis)

# Prompts
mcp.prompt(explorar_dados)
