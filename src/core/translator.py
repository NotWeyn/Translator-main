from abc import ABC, abstractmethod
import logging
import os
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TranslatorBackend(ABC):
    """Abstract base class for Translation backends."""
    
    @abstractmethod
    def translate(self, text: str, target_lang: str = 'tr', source_lang: str = 'auto') -> str:
        """
        Translate text.
        
        Args:
            text: Text to translate.
            target_lang: Target language code (e.g., 'tr', 'en').
            source_lang: Source language code (e.g., 'en', 'auto').
            
        Returns:
            Translated text string.
        """
        pass

class OpenAITranslator(TranslatorBackend):
    """Translator using OpenAI API (or compatible)."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo", base_url: Optional[str] = None):
        import openai
        self.client = openai.OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url
        )
        self.model = model

    def translate(self, text: str, target_lang: str = 'tr', source_lang: str = 'auto') -> str:
        try:
            prompt = f"Translate the following text to {target_lang}. Only output the translation, nothing else.\n\nText: {text}"
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI Translation failed: {e}")
            return text

class OfflineTranslator(TranslatorBackend):
    """Translator using Argos Translate (Offline)."""
    
    def __init__(self):
        try:
            import argostranslate.package
            import argostranslate.translate
            self.argos = argostranslate
            self.package = argostranslate.package
            self.translate_lib = argostranslate.translate
            
            # Update package index if needed (can be slow, maybe do it async or on demand)
            # self.package.update_package_index()
        except ImportError:
            logger.error("Argos Translate not installed.")
            raise
    
    def _install_lang_pair(self, from_code, to_code):
        """Attempt to install language pair if missing."""
        try:
            self.package.update_package_index()
            available_packages = self.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == from_code and x.to_code == to_code,
                    available_packages
                ), None
            )
            if package_to_install:
                logger.info(f"Installing Argos package: {from_code}->{to_code}")
                package_to_install.install()
                return True
            else:
                logger.error(f"No Argos package found for {from_code}->{to_code}")
                return False
        except Exception as e:
            logger.error(f"Failed to install Argos package: {e}")
            return False

    def translate(self, text: str, target_lang: str = 'tr', source_lang: str = 'en') -> str:
        try:
            # Argos requires specific language codes (2 letters)
            if source_lang == 'auto':
                source_lang = 'en' # Fallback, as Argos doesn't do auto-detect well natively without extra libs
            
            # Check if translation is installed
            installed_languages = self.translate_lib.get_installed_languages()
            from_lang = next((x for x in installed_languages if x.code == source_lang), None)
            to_lang = next((x for x in installed_languages if x.code == target_lang), None)
            
            if not from_lang or not to_lang:
                logger.warning(f"Languages not installed: {source_lang}->{target_lang}. Attempting download...")
                if self._install_lang_pair(source_lang, target_lang):
                     # Re-fetch installed languages
                    installed_languages = self.translate_lib.get_installed_languages()
                    from_lang = next((x for x in installed_languages if x.code == source_lang), None)
                    to_lang = next((x for x in installed_languages if x.code == target_lang), None)
            
            if from_lang and to_lang:
                translation = from_lang.get_translation(to_lang)
                if translation:
                    return translation.translate(text)
                else:
                    logger.error(f"No direct translation from {source_lang} to {target_lang}")
                    return text
            else:
                 logger.error(f"Could not find installed languages for {source_lang}->{target_lang}")
                 return text

        except Exception as e:
            logger.error(f"Offline Translation failed: {e}")
            return text

class DeepLTranslator(TranslatorBackend):
    """Translator using DeepL API."""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("DEEPL_API_KEY")
        
    def translate(self, text: str, target_lang: str = 'tr', source_lang: str = 'auto') -> str:
        import requests
        if not self.api_key:
            logger.error("DeepL API key missing.")
            return text
            
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": self.api_key,
            "text": text,
            "target_lang": target_lang.upper()
        }
        if source_lang != 'auto':
            params["source_lang"] = source_lang.upper()
            
        try:
            response = requests.post(url, data=params)
            response.raise_for_status()
            result = response.json()
            return result["translations"][0]["text"]
        except Exception as e:
            logger.error(f"DeepL Translation failed: {e}")
            return text

class GoogleTranslator(TranslatorBackend):
    """Translator using Google Translate (Unofficial/Scraping)."""
    
    def __init__(self):
        self.translator = None
        try:
            # Try to use deep_translator if available
            from deep_translator import GoogleTranslator as DeepGoogleTranslator
            self.translator = DeepGoogleTranslator
            logger.info("Google Translator initialized with deep_translator")
        except ImportError:
            logger.info("deep_translator not installed. Install with: pip install deep-translator")
            logger.info("Google Translator will return original text.")
        
    def translate(self, text: str, target_lang: str = 'tr', source_lang: str = 'auto') -> str:
        if not self.translator:
            return text
        
        try:
            # deep_translator uses different API
            translator_instance = self.translator(source='auto', target=target_lang)
            result = translator_instance.translate(text)
            return result
        except Exception as e:
            logger.error(f"Google Translation failed: {e}")
            return text

