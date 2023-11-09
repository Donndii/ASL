from googletrans import Translator

translator = Translator()

word = translator.translate("hi", dest='ru')

print(word.text)