# pip install --upgrade google-cloud-translate
from google.cloud import translate_v2


# from google.cloud import translate

def make_google_translation(text, target_language='ru', source_language='en'):
    translate_client = translate_v2.Client()
    result = translate_client.translate(text, target_language=target_language, source_language=source_language)
    return result


# def make_google_translation(text, target_language='ru', source_language='en'):
#     result = translate_text(text, target_language=target_language, source_language=source_language)
#     return result

