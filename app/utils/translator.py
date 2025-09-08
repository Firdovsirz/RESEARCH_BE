from deep_translator import GoogleTranslator

def translate_to_english(text: str, source_lang: str = "az") -> str:
    try:
        return GoogleTranslator(source=source_lang, target="en").translate(text)
    except Exception as e:
        print(f"Translation failed: {e}")
        return text