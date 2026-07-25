import sys
from pathlib import Path

# Ajouter src/ au PYTHONPATH si besoin
sys.path.insert(0, str(Path(__file__).parent.parent))

from control_tower.cli import app

if __name__ == "__main__":
    app()
