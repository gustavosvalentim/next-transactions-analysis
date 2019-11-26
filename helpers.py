import re


def clean_currency(data, value = ''):
	d = []
	for v in data:
		if 'R$' in v:
			v = v \
				.replace('R$', value) \
				.replace('.', '') \
				.replace(',', '.') \
				.strip()

		d.append(v)

	return d


def clean_tags(data, tags, value = ''):
	d = []
	for v in data:
		cleanv = v
		for t in tags:
			cleanv = re.sub(r'<{}\b[^>]*>'.format(t), value, cleanv, re.IGNORECASE)
			cleanv = re.sub(r'</{}>'.format(t), value, cleanv, re.IGNORECASE)

		d.append(cleanv)

	return d


def to_rows(raw):
	rows = str(raw).split('\n')
	a = []
	for row in rows:
		if row != '' and row != '<br/>':
			row = row \
				.replace('<br/>', '') \
				.replace('<body>', '') \
				.replace('</body>', '') \
				.replace('<hr/>', '')
			a.append(row)

	return a[2:]


def clean_empty_fields(fields):
	return [ f for f in fields if f != '' ]