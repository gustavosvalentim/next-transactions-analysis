from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from helpers import *


output_html_file_path = 'data/output.html'


with open(output_html_file_path) as htmlbuf:
	output_html_content = htmlbuf.read()

soup = BeautifulSoup(output_html_content, 'html.parser')
pages_rows = [ x for x in soup.select('body') ]
pages_rows = str(pages_rows[0]).split('\n')

rows = []
for x in pages_rows:
	if x != '' and x != '<br/>':
		x = x \
			.replace('<br/>', '') \
			.replace('<body>', '') \
			.replace('</body>', '') \
			.replace('<hr/>', '')
		rows.append(x)

rows = rows[2:]

headers_start_index = rows.index('Saldo Anterior') - 7
headers_last_index = headers_start_index + 6
data_start_index = headers_last_index + 3

headers = [ row for row in rows[headers_start_index : headers_last_index] ]
headers = clean_tags(headers, ['b'])
data = [ row for row in rows[data_start_index:] ]

days_data = ''

last_day_amount_index = 0
not_insert_index = None
for i, d in enumerate(data):
	if 'Total' in d:
		break

	if 'Saldo do Dia' in d:
		last_day_amount_index = i
		days_data += '\n'

	elif (i > last_day_amount_index + 1 and last_day_amount_index > 0) or last_day_amount_index == 0:
		if d.startswith('<b>-R$') and not data[i - 1].startswith('<b>R$'):
			days_data += '0|'

		elif i < len(data) - 1 and not d.startswith('<b>R$') and data[i + 1].startswith('<b>R$'):
			try:
				int(d)
				d = f'{d}|{data[i + i]}|0'
				not_insert_index = i + 1
			except:
				pass

		if i != not_insert_index:
			days_data += f'{d}|'

days_data_split = [ x.split('|') for x in days_data.split('\n') ]
days_data_clean_tags = [ clean_tags(x, [ 'b' ]) for x in days_data_split ]
days_data_clean_currency = [ clean_currency(x) for x in days_data_clean_tags ]
days_data_transformed = []
for row in days_data_clean_currency:
	day_transactions = []
	current_index = 0
	for i, d in enumerate(row[1:-1]):
		norm = 0
		if i == 0:
			day_transactions.append([row[0]])

		elif len(day_transactions[current_index]) + 1 == len(headers):
			day_transactions.append([row[0]])
			current_index += 1
			norm = 1

		day_transactions[current_index - norm].append(d)

	days_data_transformed.append(day_transactions[:-1])


datasource = []
for day in days_data_transformed[:-1]:
	for transaction in day:
		transaction_dict = dict([ [ headers[i], d.strip() ] for i, d in enumerate(transaction) ])
		datasource.append(transaction_dict)

last_date = ''
for i, d in enumerate(datasource):
	if d['Data'] == '':
		datasource[i]['Data'] = last_date
	else:
		last_date = d['Data']


df = pd.DataFrame(datasource)

df['Debito'] = df['Débito (R$)'] \
	.replace(regex = r'\.', value = '') \
	.replace(regex = r'\,', value = '.') \
	.replace(regex = r'\-', value = '') \
	.astype('float')

df = df.drop(columns = ['Débito (R$)'])
mes = df['Data'].str.split('/', expand = True)
df['Mes'] = mes[1]

df['MonthlyCostsAverage'] = df.groupby('Mes').Debito.transform(np.mean)
monthly_groups = df.groupby(['Mes', 'MonthlyCostsAverage']).groups
print('Valor medio de transacoes p/ mes')
print(' ' * 2 + 'Mes' + ' ' * 4 + 'Valor (R$)')
for g in monthly_groups:
	print(' ' * 2 + '%s%s%.2f' % (g[0], ' ' * 5, g[1]), end = '\n')
print()

costs_mean = df['Debito'].mean()
print(f'Valor medio de transacoes p/ dia: R$ {round(costs_mean, 2)}')

date_df = df
date_df['Count'] = 0
date_df = date_df.groupby('Data').count()

print(f'Media de transacoes p/ dia: {int(date_df.Count.mean())}')