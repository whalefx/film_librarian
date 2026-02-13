import unicodedata


def simplify_text(text):

    simplified = ''.join([c for c in unicodedata.normalize('NFKD', text) if not unicodedata.combining(c)])

    return simplified
