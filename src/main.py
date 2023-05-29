# main.py
import re
import logging
import requests_cache

from urllib.parse import urljoin
from bs4 import BeautifulSoup
from tqdm import tqdm

from constants import BASE_DIR, MAIN_DOC_URL, PEP_DOC_URL, EXPECTED_STATUS
from constants import HEADER_DICT
from configs import configure_argument_parser, configure_logging
from outputs import control_output
from utils import get_response, find_tag


def make_soup(response):
    soup = BeautifulSoup(response.text, 'lxml')
    return soup


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
    total_count = 0
    results = [(HEADER_DICT['pep'])]
    # К сожалению, совсем без заголовка тесты не пускают
    # вынос заголовка закоменчен в outputs и здесь
    if response is None:
        return
    soup = make_soup(response)
    tr_tags = soup.find_all('tr', {'class': 'row-even'})

    for tr_tag in tqdm(tr_tags):
        abbr = tr_tag.find('abbr')
        if abbr is None:
            continue
        else:
            preview_status = abbr.text[-1]
        a_tag = tr_tag.find_all('a')
        pep_url = urljoin(PEP_DOC_URL, a_tag[0]['href'])
        response_pep = get_response(session, pep_url)
        pep_soup = make_soup(response_pep)
        pep_status = pep_soup.find('abbr').text
        if preview_status not in EXPECTED_STATUS:
            logging.info(
                f'Неизвестный статус в превью {preview_status}\n {pep_url}'
                )
            continue
        if pep_status not in pep_counter.keys():
            logging.info(
                f'Неизвестный статус в карточке {pep_status}\n {pep_url}'
                )
            continue
        if pep_status not in EXPECTED_STATUS[preview_status]:
            logging.info(
                f'статус в карте {pep_status}\n '
                f'и превью {preview_status} отличается\n '
                f'{pep_url}'
                )
            continue
        pep_counter[pep_status] += 1

    for count in pep_counter.items():
        total_count += count[1]
        results.append([count[0], count[1]])
    results.append(['Total', total_count])
#    results.append(['pep'])
    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = make_soup(response)
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
        )
    results = [(HEADER_DICT['whats_new'])]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        section_response = get_response(session, version_link)
        if section_response is None:
            continue
        soup = make_soup(section_response)
        h1 = find_tag(soup, 'h1')
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
#    results.append(['whats_new'])
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = make_soup(response)
    sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [(HEADER_DICT['latest_versions'])]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        vs = re.search(pattern, a_tag.text)
        if vs is not None:
            version = vs.group('version')
            status = vs.group('status')
        else:
            version = a_tag.text
            status = ''
        results.append([link, version, status])
#    results.append(['latest_versions'])
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = make_soup(response)
    main_tag = soup.find('div', {'role': 'main'})
    table_tag = main_tag.find('table', {'class': 'docutils'})
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    if parser_mode in MODE_TO_FUNCTION:
        results = MODE_TO_FUNCTION[parser_mode](session)
    else:
        logging.info(f'Неизвестная команда {parser_mode}')
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
