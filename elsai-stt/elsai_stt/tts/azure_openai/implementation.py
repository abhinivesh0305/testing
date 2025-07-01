"""
Azure OpenAI TTS and Speech-to-Speech services.
"""

import numpy as np
import tempfile
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import io
from ...config.loggerConfig import setup_logger


class AzureOpenAITTSImplementation:
    """
    A class for converting text to speech using Azure OpenAI's TTS model.
    """

    def __init__(self, api_key: str = None, api_version: str = None, endpoint: str = None, deployment_id: str = None):
        """
        Initialize the Azure OpenAI TTS service.
        """
        self.logger = setup_logger()
        self.logger.info("Initializing Azure OpenAI TTS service")
        
        load_dotenv(override=True)
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        self.deployment_id = deployment_id
        self.logger.info(f"Azure OpenAI client initialized with deployment ID: {self.deployment_id}")

    def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        output_path: str = None,
        return_buffer: bool = False
    ) -> str | bytes | None:
        """
        Converts text to speech using Azure OpenAI's TTS model.

        Args:
            text (str): Text to convert to speech.
            voice (str, optional): Voice to use. Options: alloy, echo, fable, onyx, nova, shimmer.
            response_format (str, optional): Audio format: mp3, opus, aac, flac, wav, pcm.
            speed (float, optional): Speed of speech (0.25 to 4.0). Defaults to 1.0.
            output_path (str, optional): Path to save the audio file.
            return_buffer (bool, optional): Whether to return audio bytes instead of file path.

        Returns:
            str | bytes | None: File path if saved, audio bytes if return_buffer=True, None otherwise.

        Raises:
            ValueError: If text is empty or invalid parameters.
            RuntimeError: If speech synthesis fails.
        """
        if not text or not text.strip():
            self.logger.error("No text provided for synthesis")
            raise ValueError("Text must be provided and cannot be empty")

        if not (0.25 <= speed <= 4.0):
            self.logger.error(f"Invalid speed value: {speed}")
            raise ValueError("Speed must be between 0.25 and 4.0")

        valid_voices = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        if voice not in valid_voices:
            self.logger.error(f"Invalid voice: {voice}")
            raise ValueError(f"Voice must be one of: {', '.join(valid_voices)}")

        valid_formats = ["mp3", "opus", "aac", "flac", "wav", "pcm"]
        if response_format not in valid_formats:
            self.logger.error(f"Invalid response format: {response_format}")
            raise ValueError(f"Response format must be one of: {', '.join(valid_formats)}")

        try:
            self.logger.info(f"Synthesizing speech for text: '{text[:50]}{'...' if len(text) > 50 else ''}'")
            self.logger.info(f"Using voice: {voice}, format: {response_format}, speed: {speed}")
            
            response = self.client.audio.speech.create(
                model=self.deployment_id,
                voice=voice,
                input=text,
                response_format=response_format,
                speed=speed
            )

            audio_bytes = response.content
            self.logger.info("Speech synthesis completed successfully")

            if return_buffer:
                return audio_bytes

            if output_path:
                with open(output_path, "wb") as audio_file:
                    audio_file.write(audio_bytes)
                self.logger.info(f"Audio saved to: {output_path}")
                return output_path
            else:
                # Create temporary file
                suffix = f".{response_format}" if response_format != "pcm" else ".wav"
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_file.write(audio_bytes)
                temp_file.close()
                self.logger.info(f"Audio saved to temporary file: {temp_file.name}")
                return temp_file.name

        except Exception as e:
            self.logger.error(f"Speech synthesis failed: {str(e)}")
            raise RuntimeError(f"Speech synthesis failed: {e}")