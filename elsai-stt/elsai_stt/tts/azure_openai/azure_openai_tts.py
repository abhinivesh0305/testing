from .implementation import AzureOpenAITTSImplementation

class AzureOpenAITTS:
    """
    Wrapper class for Azure OpenAI Text-to-Speech services.
    Provides a clean interface for text-to-speech conversion.
    """
    
    def __init__(self, api_key: str = None, api_version: str = None, endpoint: str = None, deployment_id: str = None):
        """
        Initialize the Azure OpenAI TTS wrapper.
        
        Args:
            api_key (str, optional): Azure OpenAI API key
            api_version (str, optional): API version
            endpoint (str, optional): Azure OpenAI endpoint
            deployment_id (str, optional): Deployment/model ID
        """
        self._implementation = AzureOpenAITTSImplementation(
            api_key=api_key,
            api_version=api_version,
            endpoint=endpoint,
            deployment_id=deployment_id
        )
    
    def text_to_speech(
        self,
        text: str,
        voice: str = "alloy",
        format: str = "mp3",
        speed: float = 1.0,
        save_to: str = None,
        as_bytes: bool = False
    ) -> str | bytes | None:
        """
        Convert text to speech.
        
        Args:
            text (str): Text to convert to speech
            voice (str): Voice selection (alloy, echo, fable, onyx, nova, shimmer)
            format (str): Audio format (mp3, opus, aac, flac, wav, pcm)
            speed (float): Speech speed (0.25 to 4.0)
            save_to (str, optional): File path to save audio
            as_bytes (bool): Return audio as bytes instead of file path
            
        Returns:
            str | bytes | None: File path, audio bytes, or None based on parameters
        """
        return self._implementation.synthesize_speech(
            text=text,
            voice=voice,
            response_format=format,
            speed=speed,
            output_path=save_to,
            return_buffer=as_bytes
        )
    
    def create_audio_file(self, text: str, output_path: str, **kwargs) -> str:
        """
        Create an audio file from text.
        
        Args:
            text (str): Text to convert
            output_path (str): Where to save the audio file
            **kwargs: Additional parameters (voice, format, speed)
            
        Returns:
            str: Path to the created audio file
        """
        return self.text_to_speech(text=text, save_to=output_path, **kwargs)
    
    def get_audio_bytes(self, text: str, **kwargs) -> bytes:
        """
        Get audio data as bytes.
        
        Args:
            text (str): Text to convert
            **kwargs: Additional parameters (voice, format, speed)
            
        Returns:
            bytes: Audio data as bytes
        """
        return self.text_to_speech(text=text, as_bytes=True, **kwargs)