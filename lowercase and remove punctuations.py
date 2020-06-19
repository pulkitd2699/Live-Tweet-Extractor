import string
text = "Contact: 98576984. Urgent need of help in GRV, MOB."
words = text.split()
words = [word.lower() for word in words]
table = str.maketrans('','',string.punctuation)
stripped = [w.translate(table) for w in words]
text = ' '.join(stripped)
print(text)