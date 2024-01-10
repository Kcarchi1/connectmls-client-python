import re
import csv

from openpyxl import Workbook


def extract_baseurl(domains):
    for domain in domains:
        match = re.match(r'connectmls\d.mredllc.com', domain)
        if match:
            return match.group()

    return None


def convert_to_excel(name, b):
    wb = Workbook()
    ws = wb.active

    csv_reader = csv.reader(b.decode("utf-8").splitlines(), delimiter="\t")

    for row in csv_reader:
        ws.append(row)

    wb.save(f"{name}.xlsx")
    return None


def convert_to_tsv(name, b):
    lines = b.decode("utf-8").split("\n")

    with open(f"{name}.tsv", "w") as file:
        for line in lines:
            file.write(line + "\n")

    return None
