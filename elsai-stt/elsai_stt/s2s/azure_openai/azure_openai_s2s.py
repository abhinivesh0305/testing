from .implementation import AzureOpenAISpeechToSpeechImplementation 
from typing import Union

class AzureOpenAISpeechToSpeech:
    """
    Wrapper class for Azure OpenAI Speech-to-Speech service.
    Provides a clean interface over the implementation class.
    """
    
    def __init__(self, **kwargs):
        """
        Initialize the Speech-to-Speech service wrapper.
        
        Args:
            **kwargs: All arguments are passed to the underlying implementation.
                     See AzureOpenAISpeechToSpeechImplementation.__init__ for details.
        """
        self._implementation = AzureOpenAISpeechToSpeechImplementation(**kwargs)
    
    def transcribe_audio(self, **kwargs) -> str:
        """
        Transcribe audio to text.
        
        Args:
            **kwargs: Arguments passed to implementation. See transcribe_audio method for details.
            
        Returns:
            str: Transcribed text
        """
        return self._implementation.transcribe_audio(**kwargs)
    
    def synthesize_speech(self, **kwargs) -> Union[str, bytes, None]:
        """
        Convert text to speech.
        
        Args:
            **kwargs: Arguments passed to implementation. See synthesize_speech method for details.
            
        Returns:
            Union[str, bytes, None]: Audio file path, audio bytes, or None based on parameters
        """
        return self._implementation.synthesize_speech(**kwargs)
    
    def process_speech_to_speech(self, **kwargs) -> Union[str, bytes, tuple, None]:
        """
        Complete speech-to-speech conversion pipeline.
        
        Args:
            **kwargs: Arguments passed to implementation. See process_speech_to_speech method for details.
            
        Returns:
            Union[str, bytes, tuple, None]: Result based on return flags
        """
        return self._implementation.process_speech_to_speech(**kwargs)
    
    # Convenience properties for accessing implementation attributes if needed
    @property
    def whisper_deployment_id(self) -> str:
        """Get the Whisper deployment ID."""
        return self._implementation.whisper_deployment_id
    
    @property
    def tts_deployment_id(self) -> str:
        """Get the TTS deployment ID."""
        return self._implementation.tts_deployment_id
    
    @property
    def logger(self):
        """Get the logger instance."""
        return self._implementation.logger