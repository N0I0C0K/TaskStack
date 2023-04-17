from pathlib import Path

current_dir_path: Path = Path(__file__).parent.parent
config_file_path: Path = current_dir_path / "config.yaml"
db_path: Path = current_dir_path / "database.db"

output_store_path: Path = current_dir_path / ".out_store"

if not output_store_path.exists():
    print(f"create dir for {output_store_path.as_posix()}")
    output_store_path.mkdir()


def get_project_dir() -> str:
    return current_dir_path.as_posix()
