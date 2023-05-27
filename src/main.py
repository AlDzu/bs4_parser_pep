# main.py
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
    total_count = 0  # "иого" пепов
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
        pep_counter[pep_status] += 1  # счётчик статусов

    for count in pep_counter.items():
        total_count += count[1]
        results.append([count[0], count[1]])
    results.append(['Total', total_count])
    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return

    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = main_div.find('div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
        )

    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]

    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = find_tag(soup, 'h1')
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append({f'{version_link} {h1.text}, {dl_text} \n'})
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, 'lxml')
    sidebar = soup.find('div', {'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
        else:
            raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
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
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = soup.find('div', {'role': 'main'})
    table_tag = main_tag.find('table', {'class': 'docutils'})
    pdf_a4_tag = table_tag.find('a', {'href': re.compile(r'.+pdf-a4\.zip$')})
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
# Сформируйте путь до директории downloads.
    downloads_dir = BASE_DIR / 'downloads'
# Создайте директорию.
    downloads_dir.mkdir(exist_ok=True)
# Получите путь до архива, объединив имя файла с директорией.
    archive_path = downloads_dir / filename
    # Загрузка архива по ссылке.
    response = session.get(archive_url)
# В бинарном режиме открывается файл на запись по указанному пути.
    with open(archive_path, 'wb') as file:
        # Полученный ответ записывается в файл.
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    # Запускаем функцию с конфигурацией логов.
    configure_logging()
    # Отмечаем в логах момент запуска программы.
    logging.info('Парсер запущен!')
    # Конфигурация парсера аргументов командной строки —
    # передача в функцию допустимых вариантов выбора.
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    # Считывание аргументов из командной строки.
    args = arg_parser.parse_args()
    # Логируем переданные аргументы командной строки.
    logging.info(f'Аргументы командной строки: {args}')
    # Создание кеширующей сессии.
    session = requests_cache.CachedSession()
    # Если был передан ключ '--clear-cache', то args.clear_cache == True.
    if args.clear_cache:
        # Очистка кеша.
        session.cache.clear()
    # Получение из аргументов командной строки нужного режима работы.
    parser_mode = args.mode
    # Поиск и вызов нужной функции по ключу словаря.
    # MODE_TO_FUNCTION[parser_mode](session)
    results = MODE_TO_FUNCTION[parser_mode](session)

    # Если из функции вернулись какие-то результаты,
    if results is not None:
        # передаём их в функцию вывода вместе с аргументами командной строки.
        control_output(results, args)
    # Логируем завершение работы парсера.
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
