# outputs.py
import csv
import logging
import datetime as dt

from prettytable import PrettyTable

from constants import BASE_DIR, DATETIME_FORMAT  # , HEADER_DICT


def control_output(results, cli_args):
    output = cli_args.output
    if output is None:
        output = ' '
    comm_dict = {
        'pretty': pretty_output,
        'file': file_output,
        ' ': default_output,
        }
    comm_dict.get(output)(results, cli_args)


def default_output(results, cli_args):
    # results = HEADER_DICT[results[-1][0]] + results
    # del results[-1]
    for row in results:
        print(*row)


def pretty_output(results, cli_args):
    # results = HEADER_DICT[results[-1][0]] + results
    # del results[-1]
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    # del results[-1]
    results_dir = BASE_DIR / 'results'
    results_dir.mkdir(exist_ok=True)
    parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        dialect = csv.Dialect
        dialect.delimiter = ' '
        dialect.escapechar = ' '
        dialect.quoting = csv.QUOTE_NONE
        dialect.lineterminator = '\n'
        writer = csv.writer(f, dialect=dialect)
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
