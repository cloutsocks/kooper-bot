import pronouncing
import syllables
import unidecode

def process_word(original_word):

    word = unidecode.unidecode(original_word.lower())
    print(original_word, word)
    pronunciation_list = pronouncing.phones_for_word(word)
    if not pronunciation_list:
        estimate = syllables.estimate(word)
        print('Not in dict, estimate: ', estimate)
    else:
        print(pronunciation_list)
        for i, p in enumerate(pronunciation_list):
            print(f'''[{i}]: {p}, {pronouncing.syllable_count(p)}''')
    print('--')

words = '''
theatre
'''


for original_word in words.split('\n'):
    if not original_word:
        continue
    process_word(original_word)

# for word in "when is w a vowel".split(' '):
#     process_word(word)
#

