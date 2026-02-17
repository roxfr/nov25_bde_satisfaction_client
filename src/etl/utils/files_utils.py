# File: src\etl\utils\files_utils.py

"""Utilitaires pour la gestion des fichiers : lecture, écriture et suppression."""

import os
import json
import datetime
from pathlib import Path
from typing import List, Dict
from loguru import logger


class FileUtils:
    """Classe utilitaire pour la gestion de fichiers et génération de timestamps."""

    @staticmethod
    def get_timestamp() -> str:
        """Retourne un timestamp unique au format 'YYYYMMDD_HHMMSS'."""
        return datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    @staticmethod
    def create_directory_if_not_exists(path: str) -> None:
        """Crée le dossier si celui-ci n'existe pas."""
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def load_last_json(path: str) -> List[Dict]:
        """Charge le dernier fichier JSON présent dans un dossier."""
        try:
            path = Path(path)
            files = [f for f in os.listdir(path) if f.endswith(".json")]
            if not files:
                raise FileNotFoundError(f"Aucun fichier JSON trouvé dans {path}")
            files.sort(key=lambda x: os.path.getmtime(path / x), reverse=True)
            last_file = path / files[0]
            if os.path.getsize(last_file) == 0:
                raise ValueError(f"Le fichier {last_file} est vide.")
            with open(last_file, "r", encoding="utf-8") as f:
                data = []
                content = f.read().strip()
                if content:
                    try:
                        data = json.loads(content)
                    except json.JSONDecodeError as e:
                        logger.error(f"Erreur de décodage JSON dans le fichier {last_file}: {e}")
                else:
                    raise ValueError(f"Le fichier {last_file} est vide ou contient uniquement des espaces.")
                if not data:
                    raise ValueError(f"Aucune donnée valide trouvée dans {last_file}")
                return data
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du JSON {last_file if 'last_file' in locals() else path} : {e}")

    @staticmethod
    def load_last_jsonl(path: str) -> List[Dict]:
        """Charge le dernier fichier JSONL présent dans un dossier."""
        try:
            path = Path(path)
            files = [f for f in os.listdir(path) if f.endswith(".jsonl")]
            if not files:
                raise FileNotFoundError(f"Aucun fichier JSONL trouvé dans {path}")
            files.sort(key=lambda x: os.path.getmtime(path / x), reverse=True)
            last_file = path / files[0]
            with open(last_file, "r", encoding="utf-8") as f:
                return [json.loads(line) for line in f]
        except Exception as e:
            raise Exception(f"Erreur lors du chargement du JSONL {last_file if 'last_file' in locals() else path} : {e}")

    @staticmethod
    def save_to_json(data: Dict, filename: str, path: str) -> Path:
        """Enregistre un dictionnaire dans un fichier JSON avec un timestamp dans un dossier spécifique."""
        try:
            path = Path(path)
            FileUtils.create_directory_if_not_exists(path)
            filepath = path / f"{filename}_{FileUtils.get_timestamp()}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            return filepath
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde JSON {filename} : {e}")

    @staticmethod
    def save_to_jsonl(docs: List[Dict], filename: str, path: str) -> Path:
        """Enregistre une liste de dictionnaires dans un fichier JSONL avec un timestamp dans un dossier spécifique."""
        try:
            path = Path(path)
            FileUtils.create_directory_if_not_exists(path)
            filepath = path / f"{filename}_{FileUtils.get_timestamp()}.jsonl"
            with open(filepath, "w", encoding="utf-8") as f:
                for doc in docs:
                    f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            return filepath
        except Exception as e:
            raise Exception(f"Erreur lors de la sauvegarde JSONL {filename} : {e}")

    @staticmethod
    def delete_all_json_files(path: str) -> None:
        """Supprime tous les fichiers .json dans le dossier spécifié."""
        try:
            path = Path(path)
            files = [f for f in os.listdir(path) if f.endswith(".json")]
            for file in files:
                os.remove(path / file)
        except Exception as e:
            raise Exception(f"Erreur lors de la suppression des fichiers .json dans {path} : {e}")
