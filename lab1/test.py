from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer(language='russian')
# -привлекателен, но привлекательна +
#-читал
#-прочтешь


word = 'прочтут'

stem = stemmer.stem(word)
ending = word[len(stem):]

print(f'Основа: {stem}')
print(f'Окончание: {ending}')