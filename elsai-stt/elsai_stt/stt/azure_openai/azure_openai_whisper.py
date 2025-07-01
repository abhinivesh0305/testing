"""
Azure OpenAI Whisper service for speech-to-text conversion.
"""

from .implementation import AzureOpenAIWhisperImplementation
import numpy as np
import os
class AzureOpenAIWhisper:
    """
    A class for converting speech to text using Azure OpenAI's Whisper model.
    """

    def __init__(self, api_key: str = None, api_version: str = None, endpoint: str = None, deployment_id: str = None):
        """
        Initialize the Azure OpenAI Whisper service.
        """
        api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
        api_version = api_version or os.getenv("AZURE_OPENAI_API_VERSION")
        endpoint = endpoint or os.getenv("AZURE_OPENAI_ENDPOINT")
        deployment_id = deployment_id or os.getenv("AZURE_OPENAI_DEPLOYMENT_ID")
        print(deployment_id)
        if not all([api_key, api_version, endpoint, deployment_id]):
            raise ValueError("All parameters (api_key, api_version, endpoint, deployment_id) must be provided or set in environment variables AZURE_OPENAI_API_KEY, AZURE_OPENAI_API_VERSION, AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_DEPLOYMENT_ID.")

        self._impl= AzureOpenAIWhisperImplementation(
            api_key=api_key,
            api_version=api_version,
            endpoint=endpoint,
            deployment_id=deployment_id
        )

    def transcribe_audio(
        self,
        file_path: str = None,
        buffer: list[np.ndarray] = None,
        output_format: str = "webm",
        sample_rate: int = 24000
    ) -> str:
        """
        Transcribes audio either from a file or from a list of audio buffers.

        Args:
            file_path (str, optional): Path to the audio file to transcribe.
            buffer (list[np.ndarray], optional): List of float32 numpy audio arrays.
            output_format (str, optional): Desired output format: 'webm', 'wav', or 'mp3'.
            sample_rate (int, optional): Sample rate of the audio. Defaults to 24000.

        Returns:
            str: Transcribed text from the audio.

        Raises:
            ValueError: If neither file_path nor buffer is provided.
            RuntimeError: If transcription fails.
        """
        return self._impl.transcribe_audio(
            file_path=file_path,
            buffer=buffer,
            output_format=output_format,
            sample_rate=sample_rate
        )
