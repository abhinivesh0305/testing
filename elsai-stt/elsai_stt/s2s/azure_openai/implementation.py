"""
Azure OpenAI Speech-to-Speech service combining Whisper (STT) and TTS capabilities.
"""

import numpy as np
import tempfile
import os
from openai import AzureOpenAI
from dotenv import load_dotenv
from pydub import AudioSegment
import io
from typing import Optional, Union, List
from ...config.loggerConfig import setup_logger


class AzureOpenAISpeechToSpeechImplementation:
    """
    Implementation class for converting speech to speech using Azure OpenAI's Whisper and TTS models.
    This combines speech-to-text transcription with text-to-speech synthesis.
    """

    def __init__(
                    self, 
                    api_key: str = None, 
                    api_version: str = None, 
                    endpoint: str = None, 
                    whisper_deployment_id: str = None,
                    tts_deployment_id: str = None,
                    whisper_api_key: str = None,
                    whisper_api_version: str = None,
                    whisper_endpoint: str = None,
                    tts_api_key: str = None,
                    tts_api_version: str = None,
                    tts_endpoint: str = None
                ):
        self.logger = setup_logger()
        self.logger.info("Initializing Azure OpenAI Speech-to-Speech service")
        load_dotenv(override=True)

        self._validate_required_deployments(whisper_deployment_id, tts_deployment_id)

        use_separate_configs = any([
            whisper_api_key, whisper_api_version, whisper_endpoint,
            tts_api_key, tts_api_version, tts_endpoint
        ])

        shared_config = {
            "key": api_key,
            "version": api_version,
            "endpoint": endpoint
        }

        whisper_config = {
            "key": whisper_api_key,
            "version": whisper_api_version,
            "endpoint": whisper_endpoint
        }

        tts_config = {
            "key": tts_api_key,
            "version": tts_api_version,
            "endpoint": tts_endpoint
        }

        self._setup_clients(use_separate_configs, shared_config, whisper_config, tts_config)

        self.whisper_deployment_id = whisper_deployment_id
        self.tts_deployment_id = tts_deployment_id

        self.logger.info(f"Speech-to-Speech service initialized:")
        self.logger.info(f"  - Whisper STT deployment: {self.whisper_deployment_id}")
        self.logger.info(f"  - TTS deployment: {self.tts_deployment_id}")

    def _validate_required_deployments(self, whisper_id: str, tts_id: str):
        if not whisper_id:
            raise ValueError("whisper_deployment_id is required for speech-to-text functionality")
        if not tts_id:
            raise ValueError("tts_deployment_id is required for text-to-speech functionality")

    def _setup_clients(
        self,
        use_separate: bool,
        shared_config: dict,
        whisper_config: dict,
        tts_config: dict
    ):
        if use_separate:
            self.logger.info("Using separate configurations for Whisper and TTS")

            whisper_key = whisper_config.get("key") or shared_config["key"]
            whisper_ver = whisper_config.get("version") or shared_config["version"]
            whisper_ep = whisper_config.get("endpoint") or shared_config["endpoint"]

            if not all([whisper_key, whisper_ver, whisper_ep]):
                raise ValueError("Whisper configuration incomplete.")

            self.whisper_client = AzureOpenAI(
                api_key=whisper_key,
                api_version=whisper_ver,
                azure_endpoint=whisper_ep,
            )

            tts_key = tts_config.get("key") or shared_config["key"]
            tts_ver = tts_config.get("version") or shared_config["version"]
            tts_ep = tts_config.get("endpoint") or shared_config["endpoint"]

            if not all([tts_key, tts_ver, tts_ep]):
                raise ValueError("TTS configuration incomplete.")

            self.tts_client = AzureOpenAI(
                api_key=tts_key,
                api_version=tts_ver,
                azure_endpoint=tts_ep,
            )

            self.client = self.whisper_client

            self.logger.info(f"Whisper client configured with endpoint: {whisper_ep}")
            self.logger.info(f"TTS client configured with endpoint: {tts_ep}")
        else:
            self.logger.info("Using shared configuration for Whisper and TTS")

            if not all(shared_config.values()):
                raise ValueError("Shared configuration incomplete. Need api_key, api_version, and endpoint")

            self.client = AzureOpenAI(**{
                "api_key": shared_config["key"],
                "api_version": shared_config["version"],
                "azure_endpoint": shared_config["endpoint"]
            })
            self.whisper_client = self.client
            self.tts_client = self.client

            self.logger.info(f"Shared client configured with endpoint: {shared_config['endpoint']}")

    def transcribe_audio(
        self,
        file_path: str = None,
        buffer: List[np.ndarray] = None,
        output_format: str = "webm",
        sample_rate: int = 24000
    ) -> str:
        """
        Transcribes audio either from a file or from a list of audio buffers.
        """
        if not file_path and not buffer:
            self.logger.error("No audio source provided for transcription")
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
                result = self.whisper_client.audio.transcriptions.create(
                    file=audio_file,
                    model=self.whisper_deployment_id
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

    def synthesize_speech(
        self,
        text: str,
        voice: str = "alloy",
        response_format: str = "mp3",
        speed: float = 1.0,
        output_path: str = None,
        return_buffer: bool = False
    ) -> Union[str, bytes, None]:
        """
        Converts text to speech using Azure OpenAI's TTS model.
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
            
            response = self.tts_client.audio.speech.create(
                model=self.tts_deployment_id,
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

    def process_speech_to_speech(
        self,
        input_file_path: str = None,
        input_buffer: List[np.ndarray] = None,
        input_format: str = "webm",
        input_sample_rate: int = 24000,
        output_voice: str = "alloy",
        output_format: str = "mp3",
        output_speed: float = 1.0,
        output_path: str = None,
        return_buffer: bool = False,
        text_processor: callable = None,
        return_transcription: bool = False
    ) -> Union[str, bytes, tuple, None]:
        """
        Complete speech-to-speech conversion pipeline.
        
        Args:
            input_file_path (str, optional): Path to input audio file
            input_buffer (List[np.ndarray], optional): List of audio buffers
            input_format (str): Format for processing input buffer ('webm', 'wav', 'mp3')
            input_sample_rate (int): Sample rate for input buffer processing
            output_voice (str): Voice for TTS output ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
            output_format (str): Output audio format ('mp3', 'opus', 'aac', 'flac', 'wav', 'pcm')
            output_speed (float): Speed of output speech (0.25 to 4.0)
            output_path (str, optional): Path to save output audio
            return_buffer (bool): Whether to return audio bytes instead of file path
            text_processor (callable, optional): Function to process transcribed text before TTS
            return_transcription (bool): Whether to return transcription along with audio
            
        Returns:
            str | bytes | tuple | None: Depends on return_buffer and return_transcription flags
            
        Raises:
            ValueError: If input parameters are invalid
            RuntimeError: If speech processing fails
        """
        try:
            # Step 1: Transcribe input speech to text
            self.logger.info("Starting speech-to-speech conversion")
            self.logger.info("Step 1: Transcribing input speech")
            
            transcribed_text = self.transcribe_audio(
                file_path=input_file_path,
                buffer=input_buffer,
                output_format=input_format,
                sample_rate=input_sample_rate
            )
            
            self.logger.info(f"Transcription result: '{transcribed_text[:100]}{'...' if len(transcribed_text) > 100 else ''}'")
            
            # Step 2: Process text if processor is provided
            processed_text = transcribed_text
            if text_processor and callable(text_processor):
                self.logger.info("Step 2: Processing transcribed text")
                try:
                    processed_text = text_processor(transcribed_text)
                    self.logger.info(f"Processed text: '{processed_text[:100]}{'...' if len(processed_text) > 100 else ''}'")
                except Exception as e:
                    self.logger.warning(f"Text processing failed, using original text: {str(e)}")
                    processed_text = transcribed_text
            
            # Step 3: Convert processed text back to speech
            self.logger.info("Step 3: Converting text to speech")
            
            result = self.synthesize_speech(
                text=processed_text,
                voice=output_voice,
                response_format=output_format,
                speed=output_speed,
                output_path=output_path,
                return_buffer=return_buffer
            )
            
            self.logger.info("Speech-to-speech conversion completed successfully")
            
            # Return based on flags
            if return_transcription:
                return (result, transcribed_text, processed_text)
            else:
                return result
                
        except Exception as e:
            self.logger.error(f"Speech-to-speech conversion failed: {str(e)}")
            raise RuntimeError(f"Speech-to-speech conversion failed: {e}")

