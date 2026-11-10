"""MCP server exposing verify_citation over stdio (ADR-0015).

Same capability as the HTTP route (`app/tools/citation_verify.py`), exposed as an MCP
tool with the JSON schema from `[220]`. The `mcp` SDK is imported lazily so the rest
of the app does not depend on it. Run as: ``python -m app.tools.mcp_server``.
"""

from __future__ import annotations

from typing import Any

from app.tools.citation_verify import CitationVerifierAdapter


def build_server() -> Any:
    """Construct the MCP stdio server and register the verify_citation tool."""
    from mcp.server.fastmcp import FastMCP  # deferred: MCP SDK

    server = FastMCP("leon-tools")
    verifier = CitationVerifierAdapter()

    @server.tool()
    def verify_citation(locator: str, quoted_text: str | None = None) -> dict[str, Any]:
        """Check whether a cited section/clause exists in the source documents ([220])."""
        result = verifier.verify(locator, quoted_text)
        return {
            "exists": result.exists,
            "source_document": result.source_document,
            "matched_passage": result.matched_passage,
        }

    return server


def main() -> None:  # pragma: no cover - process entrypoint
    build_server().run(transport="stdio")


if __name__ == "__main__":  # pragma: no cover
    main()
