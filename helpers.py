def clean_currency(data, value = ''):
	d = []
	for v in data:
		if 'R$' in v:
			v = v.replace('R$', value)

		d.append(v)

	return d


def clean_tags(data, tags, value = ''):
	d = []
	for v in data:
		for t in tags:
			v = v \
				.replace(f'<{t}>', value) \
				.replace(f'</{t}>', value)
			d.append(v)

	return d