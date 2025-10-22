from synth_datasets import csvgenerator, htmlgenerator, xmlgenerator, jsongenerator

def generate_datasets(rows_total: int):
    parted = rows_total // 4
    csvgenerator.generate(rows=parted)
    htmlgenerator.generate(rows=parted)
    xmlgenerator.generate(rows=parted)
    jsongenerator.generate(rows=parted)