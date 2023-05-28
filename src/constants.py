# constants.py
from pathlib import Path

MAIN_DOC_URL = 'https://docs.python.org/3/'
PEP_DOC_URL = 'https://peps.python.org/'
BASE_DIR = Path(__file__).parent
LOG_DIR = Path(__file__).parent / 'logs'
RESULTS_DIR = Path(__file__).parent / 'results'
LOG_FILE = Path(__file__).parent / 'logs' / 'parser.log'
DATETIME_FORMAT = '%Y-%m-%d_%H-%M-%S'
EXPECTED_STATUS = {
    'A': ('Active', 'Accepted'),
    'D': ('Deferred',),
    'F': ('Final',),
    'P': ('Provisional',),
    'R': ('Rejected',),
    'S': ('Superseded',),
    'W': ('Withdrawn',),
    '': ('Draft', 'Active'),
}
HEADER_DICT = {
    'latest_versions': (('Ссылка на документацию'), ('Версия'), ('Статус')),
    'pep': (('Статус'), ('Количество')),
    'whats_new': (('Ссылка на статью'), ('Заголовок'), ('Редактор, Автор'))
    }
