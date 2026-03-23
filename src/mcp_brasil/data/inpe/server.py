"""INPE feature server — registers tools, resources, and prompts.

This file only registers components. Zero business logic (ADR-001 rule #4).
"""

from fastmcp import FastMCP

from .prompts import monitoramento_ambiental
from .resources import biomas_brasileiros, estados_amazonia_legal
from .tools import alertas_deter, buscar_focos_queimadas, consultar_desmatamento, dados_satelite

mcp = FastMCP("mcp-brasil-inpe")

# Tools
mcp.tool(buscar_focos_queimadas)
mcp.tool(consultar_desmatamento)
mcp.tool(alertas_deter)
mcp.tool(dados_satelite)

# Resources (URIs without namespace prefix — mount adds "inpe/" automatically)
mcp.resource("data://biomas", mime_type="application/json")(biomas_brasileiros)
mcp.resource("data://amazonia-legal", mime_type="application/json")(estados_amazonia_legal)

# Prompts
mcp.prompt(monitoramento_ambiental)
