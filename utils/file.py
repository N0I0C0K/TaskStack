from pathlib import Path

current_dir_path: Path = Path(__file__).parent.parent
config_file_path: Path = current_dir_path / "config.yaml"
db_path: Path = current_dir_path / "database.db"


def get_project_dir() -> str:
    return current_dir_path.as_posix()
