#Script to test if the translate library is working
from googletrans import Translator

trans = Translator()

sentence = "Je suis un homme"

#If googletrans is working this will print "I am a man"
translated = trans.translate(sentence)
if translated == 'I am a man':
    print(sentence, ': Working correctly')
else:
    print(sentence, ': Not translated')