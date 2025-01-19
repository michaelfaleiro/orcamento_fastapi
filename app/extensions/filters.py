# filepath: /Users/michaelfaleiro/Projetos/Python/orcamento/app/extensions/filters.py
def format_currency(value):
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

# Adicione o filtro ao ambiente Jinja2
from jinja2 import Environment

def environment(**options):
    env = Environment(**options)
    env.filters['currency'] = format_currency
    return env