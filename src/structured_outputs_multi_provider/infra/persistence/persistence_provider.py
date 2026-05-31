import csv
from datetime import datetime
from pathlib import Path
from typing import List

from structured_outputs_multi_provider.infra.persistence.interfaces.persistence_provider import (
    IPersistenceProvider,
)

ROOT_DIR = Path(__file__).parent.parent.parent.parent.parent


class PersistenceProvider(IPersistenceProvider):
    def save_many(self, headers: List[str], data: List[dict]) -> None:
        output_path = Path(
            f"{ROOT_DIR}/data/result_{int(datetime.now().timestamp())}.csv"
        )
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with output_path.open(mode="w", newline="", encoding="utf-8") as output_file:
            writer = csv.DictWriter(output_file, headers)
            writer.writeheader()
            writer.writerows(data)
