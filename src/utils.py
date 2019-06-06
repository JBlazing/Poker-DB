from tabulate import tabulate

def format_table(sessions , headers):
    print (tabulate(sessions , headers=headers))