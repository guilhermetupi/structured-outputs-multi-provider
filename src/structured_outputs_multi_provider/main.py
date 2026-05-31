import argparse
import asyncio

from structured_outputs_multi_provider.dependencies.services.bench import bench_service
from structured_outputs_multi_provider.dependencies.services.chain import chain_service


async def main():
    print("Welcome to Structured Outputs Multi Provider")

    parser = argparse.ArgumentParser(
        description="Structured Outputs Multi Provider CLI"
    )
    parser.add_argument(
        "--bench",
        action="store_true",
        default=False,
        help="Bench mode. Compare all LLMs adapters.",
    )
    parser.add_argument("--prompt", type=str, help="User prompt.")
    args = parser.parse_args()

    if args.bench:
        await bench_service.execute(args.prompt)
    else:
        await chain_service.execute(args.prompt)


if __name__ == "__main__":
    asyncio.run(main())
