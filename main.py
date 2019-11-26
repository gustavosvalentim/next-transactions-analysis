from os import path

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib


matplotlib.use('TkAgg')



ROOTDIR = path.abspath(path.dirname(__file__))
DATADIR = path.join(ROOTDIR, 'output')


df = pd.read_csv(path.join(DATADIR, 'transactions.csv'))
datesplit = df.Data.str.split('/', expand = True)

df.loc[:, 'Dia'] = datesplit[0]
df.loc[:, 'Mes'] = datesplit[1]

# transactionspday = dftransactions
# transactionspday = transactionspday.groupby(['Dia', 'Mes']).size().reset_index(name = 'Count')
# transactionspday = transactionspday[ transactionspday['Mes'] == '11' ]
# counting = transactionspday['Count'].values
# countarray = np.array(counting).mean()
# days = transactionspday['Dia'].values
# months = transactionspday['Mes'].values

# daymonth = [ f'{x}/{months[i]}' for i, x in enumerate(days) ]

# plt.bar(daymonth, counting)
# plt.axhline(countarray)
# plt.show()

costspmonth = df[ (df['Débito (R$)'] != '0') & (df['Mes'] == '08') ]
costspmonth.loc[:, 'Debito'] = costspmonth['Débito (R$)'] \
	.str.replace('-', '') \
	.str.strip() \
	.astype('float')

costsbyday = costspmonth.groupby(['Dia', 'Mes']).agg({ 'Debito': ['sum'] })
dates = []
for day, month in costsbyday.index:
	dates.append(f'{day}-{month}')

debits = costsbyday['Debito'].to_numpy()
debits = [ x for x in list(debits) ]
stddebits = np.std([ v for v in debits ])

for d in dates:
	plt.axvline(d, linestyle = ':')

plt.axhline(np.mean(debits), color = 'r', linestyle = ':')

plt.plot(dates, debits, 'c--')
plt.plot(dates, debits, 'bo')
plt.show()