# migrations/seeds/runner.py
"""CLI unificada para seeds. Uso: python -m migrations.seeds.runner [dev|staging|test]"""
import argparse
import asyncio
import os
import sys

# Asegurar que el directorio src esté en el PYTHONPATH si no se corre desde docker con él
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../src")))

SEEDS = {
    "dev":     "migrations.seeds.development",
    "staging": "migrations.seeds.staging",
    "test":    "migrations.seeds.testing",
}

async def _run(module_path: str) -> None:
    import importlib
    mod = importlib.import_module(module_path)
    seed_fn = getattr(mod, "seed", None)
    if seed_fn:
        await seed_fn()
    else:
        print(f"⚠️  {module_path} no tiene función seed() asíncrona")

def main() -> None:
    """Ejecuta la CLI de semillas de base de datos."""
    env = os.getenv("APP_ENV", "dev")
    parser = argparse.ArgumentParser()
    parser.add_argument("environment", nargs="?", default=env, choices=SEEDS.keys())
    args = parser.parse_args()
    asyncio.run(_run(SEEDS[args.environment]))

if __name__ == "__main__":
    main()
