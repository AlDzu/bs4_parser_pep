import re
import logging
import requests_cache

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


session = requests_cache.CachedSession()
response = session.get(PEP_DOC_URL)


def pep(session):
    response = get_response(session, PEP_DOC_URL)
    pep_counter = {
        'Active': 0,
        'Accepted': 0,
        'Deferred': 0,
        'Final': 0,
        'Provisional': 0,
        'Rejected': 0,
        'Superseded': 0,
        'Withdrawn': 0,
        'Draft': 0,
        'Active': 0,
    }
    total_count = 0 # "иого" пепов
    results = [('Статус', 'Количество')]
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    tr_tags = soup.find_all('tr', {'class': 'row-even'})

    for tr_tag in tqdm(tr_tags):
        abbr = tr_tag.find('abbr')
        if abbr is None:
            continue
        else:
            preview_status = abbr.text[-1]  # статус из превью
        a_tag = tr_tag.find_all('a')
        # pep_numder = a_tag[0].text  # номер пепа
        # pep_title = a_tag[1].text # название пепа
        pep_url = urljoin(PEP_DOC_URL, a_tag[0]['href'])  # ссылка на пеп
        response_pep = get_response(session, pep_url)
        pep_soup = BeautifulSoup(response_pep.text, 'lxml')
        pep_status = pep_soup.find('abbr').text  # статус пепа из карточки
        if preview_status not in EXPECTED_STATUS:
            print(f'Неизвестный статус в превью {preview_status}')
            continue
        if pep_status not in pep_counter.keys():
            print(f'Неизвестный статус в карточке {pep_status}')
            continue
        if pep_status not in EXPECTED_STATUS[preview_status]:
            print('статус в карте и превью отличается')
            continue
        pep_counter[pep_status] += 1  # счётчик статусов

    for count in pep_counter.items():
        total_count += count[1]
        results.append([count[0], count[1]])
    results.append(['Total', total_count])
    return results

pep(session)
