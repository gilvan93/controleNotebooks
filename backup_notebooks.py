
import shutil
from datetime import datetime
from pathlib import Path

# Caminho da pasta principal do sistema
PASTA_PROJETO = Path(__file__).resolve().parent

# Arquivo original e pasta de backups
ARQUIVO_ORIGINAL = PASTA_PROJETO / "notebooks.json"
PASTA_BACKUPS = PASTA_PROJETO / "backups"

# Cria a pasta de backups, caso não exista
PASTA_BACKUPS.mkdir(exist_ok=True)

# Verifica se o arquivo original existe
if not ARQUIVO_ORIGINAL.exists():
    raise FileNotFoundError(
        f"Arquivo não encontrado: {ARQUIVO_ORIGINAL}"
    )

# Cria um nome com data e horário
data_hora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
ARQUIVO_BACKUP = PASTA_BACKUPS / f"notebooks_{data_hora}.json"

# Copia o arquivo original
shutil.copy2(ARQUIVO_ORIGINAL, ARQUIVO_BACKUP)

print(f"Backup criado com sucesso: {ARQUIVO_BACKUP}")
