def as_text(value):
	if value is None:
		return ""
	else:
		return str(value)

def index_to_letter(index):
	return chr(64 + (index % 26))

