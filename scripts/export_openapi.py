#!/usr/bin/env python3
"""
Exports OpenAPI JSON specification directly from the FastAPI application instance.
This avoids needing a live backend server process running to generate contracts.
"""
import importlib
import json
import os
import sys


def main() -> None:
    """Export the FastAPI OpenAPI schema to packages/api-client/openapi.json."""
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    api_dir = os.path.join(repo_root, "apps", "api")
    if api_dir not in sys.path:
        sys.path.insert(0, api_dir)

    try:
        main_module = importlib.import_module("app.main")
        fastapi_app = getattr(main_module, "app")
        openapi_spec = fastapi_app.openapi()
        output_path = os.path.join(repo_root, "packages", "api-client", "openapi.json")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(openapi_spec, f, indent=2)
        print(f"Successfully generated OpenAPI schema at: {output_path}")
    except Exception as exc:
        print(f"Error exporting OpenAPI specification: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
