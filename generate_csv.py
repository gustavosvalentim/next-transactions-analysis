from bs4 import BeautifulSoup
import pandas as pd
import re

from helpers import *


output_html_file_path = 'data/output.html'


with open(output_html_file_path) as htmlbuf:
	output_html_content = htmlbuf.read()

soup = BeautifulSoup(output_html_content, 'html.parser')
raw = soup.select('body')
rows = to_rows(raw)

headers_start_index = rows.index('Saldo Anterior') - 7
headers_last_index = headers_start_index + 6
data_start_index = headers_last_index + 3

headers = [ row for row in rows[headers_start_index : headers_last_index] ]
headers = clean_tags(headers, [ 'b' ])

datasource = rows[data_start_index:]
cleantags = clean_tags(datasource, [ 'b', 'a' ])
cleancurrency = clean_currency(cleantags)
rememptyfields = clean_empty_fields(cleancurrency)

datepattern = r'([0-9]{2}/[0-9]{2}/[0-9]{4})'
dateindexes = [ i for i, d in enumerate(rememptyfields) if re.search(datepattern, d) ]
datetransactions = [ rememptyfields[x:dateindexes[i + 1]] for i, x in enumerate(dateindexes[:-1]) ]

total_index = datetransactions[-1].index('Total')
totals = datetransactions[-1][total_index + 1:]
remtotals = [ *datetransactions[:-1], datetransactions[-1][:total_index] ]

day_amounts = {}
for i, d in enumerate(remtotals):
	amount_index = d.index('Saldo do Dia')
	day_amounts[d[0]] = remtotals[i][amount_index + 1]
	remtotals[i] = remtotals[i][:amount_index]

datetransactionsdict = dict([ [ x[0], x[1:] ] for x in remtotals ])

datetransactionsarray = []
for d, t in datetransactionsdict.items():
	arraytransactions = []
	if len(t) == 3:
		print(datetransactionsdict[d], 'oi')
		exit()
	for i, v in enumerate(t):
		current_index = len(arraytransactions)
		if i % 4 == 0 or i == 0:
			arraytransactions.append([d, v])

		else:
			arraytransactions[current_index - 1].append(v)

	for transaction in arraytransactions:
		datetransactionsarray.append(transaction)

transactionsdata = []
for transaction in datetransactionsarray:
	transactionproc = []
	if transaction[3].startswith('-'):
		transactionproc = [ *transaction[:3], 0, transaction[3], transaction[4] ]
	else:
		transactionproc = [ *transaction[:3], transaction[3], 0, transaction[4] ]

	transactionsdata.append(transactionproc)

transactionsrows = [ dict([ [ headers[i], v ] for i, v in enumerate(transaction) ]) for transaction in transactionsdata ]

totals_headers = headers[3:]
totalsrows = dict([ [ totals_headers[i], v ] for i, v in enumerate(totals) ])

dayamountrows = [ dict({ 'Data': d, 'Saldo (R$)': dayamount }) for d, dayamount in day_amounts.items() ]

dftransactions = pd.DataFrame(transactionsrows).to_csv('output/transactions.csv', index = False)
dfdayamount = pd.DataFrame(dayamountrows).to_csv('output/day-amount.csv', index = False)
dftotals = pd.DataFrame([totalsrows]).to_csv('output/totals.csv', index = False)