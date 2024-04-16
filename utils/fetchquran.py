import requests
import datetime

from utils.gui import set_timezone
from utils.database import ServerSetTransaltion

set_timezone = set_timezone


class FetchQuran:
    async def fetch_quran(self, server_id: int, verse: int, chapter: int=None):
                
            servertranslation = ServerSetTransaltion(server_id)
            translation_key = await servertranslation.load()
            current_time = datetime.datetime.now(set_timezone)

            if chapter is not None:
                url = f'http://api.alquran.cloud/ayah/{chapter}:{verse}/editions/quran-uthmani,{translation_key}'
            else:
                url = f'http://api.alquran.cloud/ayah/{verse}/editions/quran-uthmani,{translation_key}'

            print(f"At {current_time.strftime('%H:%M %p on %d-%m-%Y')}, Invoked Random Quran Verse API URL: {url}") #for debugging
            response = requests.get(url)
                
            if response.status_code != 200:
                print(f"Failed to fetch verse data: {response.status_code}")
                return None 
                
            json_data = requests.get(url).json()

            verse_arabic = json_data['data'][0]['text']
            verse_translation = json_data['data'][1]['text']
            surah_name = json_data['data'][0]['surah']['englishName']
            surah_name_english = json_data['data'][0]['surah']['englishNameTranslation']
            translation_name_english = json_data['data'][1]['edition']['englishName']
            number_in_surah = json_data['data'][0]['numberInSurah']
            chapter_number = json_data['data'][0]['surah']['number']
            sajda = json_data['data'][0]['sajda']

            sajda_info = "Sajda is Wajib" if sajda else ""

            return {
                'verse_arabic': verse_arabic,
                'verse_translation': verse_translation,
                'surah_name': surah_name,
                'number_in_surah': number_in_surah,
                'surah_name_english': surah_name_english,
                'translation_name_english': translation_name_english,
                'chapter_number': chapter_number,
                'sajda_info': sajda_info
                }