"""
Azure OpenAI Whisper service for speech-to-text conversion.
"""

import numpy as np
import tempfile
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import io
from ...config.loggerConfig import setup_logger


class AzureOpenAIWhisperImplementation:
    """
    A class for converting speech to text using Azure OpenAI's Whisper model.
    """

    def __init__(self, api_key: str = None, api_version: str = None, endpoint: str = None, deployment_id: str = None):
        """
        Initialize the Azure OpenAI Whisper service.
        """
        self.logger = setup_logger()
        self.logger.info("Initializing Azure OpenAI Whisper service")
        
        load_dotenv(override=True)
        
        self.client = AzureOpenAI(
            api_key=api_key,
            api_version=api_version,
            azure_endpoint=endpoint,
        )
        self.deployment_id = deployment_id
        self.logger.info(f"Azure OpenAI client initialized with deployment ID: {self.deployment_id}")

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
        if not file_path and not buffer:
            self.logger.error("No audio source provided")
            raise ValueError("Either file_path or buffer must be provided")

        if buffer:
            self.logger.info(f"Processing audio buffer with {len(buffer)} chunks")
            try:
                # Concatenate and normalize audio
                audio_data = np.concatenate(buffer)
                audio_data = np.clip(audio_data, -1.0, 1.0)
                pcm_audio = np.int16(audio_data * 32767)

                # Convert to AudioSegment
                audio_segment = AudioSegment(
                    pcm_audio.tobytes(),
                    frame_rate=sample_rate,
                    sample_width=2,
                    channels=1
                )

                # Export to specified format
                self.logger.info(f"Converting audio to {output_format} format")
                buffer_io = io.BytesIO()
                if output_format == "webm":
                    audio_segment.export(buffer_io, format="webm", codec="libopus", bitrate="64k")
                    suffix = ".webm"
                elif output_format == "wav":
                    audio_segment.export(buffer_io, format="wav")
                    suffix = ".wav"
                elif output_format == "mp3":
                    audio_segment.export(buffer_io, format="mp3", bitrate="64k")
                    suffix = ".mp3"
                else:
                    self.logger.error(f"Unsupported format: {output_format}")
                    raise ValueError("Unsupported format. Use 'webm', 'wav', or 'mp3'.")

                audio_bytes = buffer_io.getvalue()
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
                temp_file.write(audio_bytes)
                temp_file.close()
                audio_path = temp_file.name
                self.logger.debug(f"Temporary audio file created at: {audio_path}")

            except Exception as e:
                self.logger.error(f"Buffer conversion failed: {str(e)}")
                raise RuntimeError(f"Buffer conversion failed: {e}")
        else:
            self.logger.info(f"Using provided audio file: {file_path}")
            audio_path = file_path

        try:
            self.logger.info("Sending audio to Azure OpenAI Whisper for transcription")
            with open(audio_path, "rb") as audio_file:
                result = self.client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.deployment_id
                )
            self.logger.info("Transcription completed successfully")
            return result.text
        except Exception as e:
            self.logger.error(f"Transcription failed: {str(e)}")
            raise RuntimeError(f"Transcription failed: {e}")
        finally:
            if buffer and os.path.exists(audio_path):
                self.logger.debug(f"Cleaning up temporary file: {audio_path}")
                os.remove(audio_path)
