"""DataJud feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import analise_processo, pesquisa_juridica
from .resources import classes_processuais, info_api, tribunais_disponiveis
from .tools import (
    buscar_processo_por_numero,
    buscar_processos,
    buscar_processos_avancado,
    buscar_processos_por_assunto,
    buscar_processos_por_classe,
    buscar_processos_por_orgao,
    consultar_movimentacoes,
)

mcp = FastMCP("mcp-brasil-datajud")

# Tools (7)
mcp.tool(buscar_processos)
mcp.tool(buscar_processo_por_numero)
mcp.tool(buscar_processos_por_classe)
mcp.tool(buscar_processos_por_assunto)
mcp.tool(buscar_processos_por_orgao)
mcp.tool(buscar_processos_avancado)
mcp.tool(consultar_movimentacoes)

# Resources
mcp.resource("data://tribunais", mime_type="application/json")(tribunais_disponiveis)
mcp.resource("data://classes-processuais", mime_type="application/json")(classes_processuais)
mcp.resource("data://info-api", mime_type="application/json")(info_api)

# Prompts
mcp.prompt(analise_processo)
mcp.prompt(pesquisa_juridica)
