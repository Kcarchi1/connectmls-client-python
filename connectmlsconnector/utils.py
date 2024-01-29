import re
import csv
from os import path

from openpyxl import Workbook


def extract_baseurl(domains):
    for domain in domains:
        match = re.match(r'connectmls\d.mredllc.com', domain)
        if match:
            return match.group()

    return None


def focus_keys(input_dict: dict, keys: list) -> dict:
    return {key: input_dict[key] for key in keys if key in input_dict}


def convert_to_excel(save_path: str, name: str, b: bytes):
    if save_path is not None:
        save_path = path.join(save_path, name)
    else:
        save_path = name

    wb = Workbook()
    ws = wb.active

    csv_reader = csv.reader(b.decode("utf-8").splitlines(), delimiter="\t")

    for row in csv_reader:
        ws.append(row)

    wb.save(f"{save_path}.xlsx")


def convert_to_tsv(save_path: str, name: str, b: bytes):
    if save_path is not None:
        save_path = path.join(save_path, name)
    else:
        save_path = name

    lines = b.decode("utf-8").split("\n")

    with open(f"{save_path}.tsv", "w") as file:
        for line in lines:
            file.write(line + "\n")