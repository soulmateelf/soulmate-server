from typing import Union

import speech_recognition as sr
import pyttsx3
import uuid
from azure.cognitiveservices.speech.audio import AudioOutputConfig
import os
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig, ResultReason, audio
from elevenlabs import set_api_key, generate, Voice, Model, save
from elevenlabs.api import voice
from pydub import AudioSegment

from soulmate_server.conf.systemConf import file_path, fileSrc


def mp3_to_text(file_path):
    # 创建一个Recognizer对象
    recognizer = sr.Recognizer()

    with sr.AudioFile(file_path) as source:
        audi1o = recognizer.record(source)

    try:
        # 使用Google语音识别将音频转换为文本
        text = recognizer.recognize_google(audi1o)  # 指定语言为中文
        print("识别结果：", text)
        return text
    except sr.UnknownValueError:
        return "无法识别音频"
    except sr.RequestError as e:
        return "无法识别音频"


def text_t():
    # 初始化TTS引擎
    engine = pyttsx3.init()

    # 合成文本
    text = "kanye west is my bro "
    engine.say(text)
    engine.setProperty('rate', 40)
    voices = engine.getProperty('voices')
    print(f'语音声音详细信息：{voices}')
    engine.setProperty('voice', voices[1].id)
    # 播放语音
    engine.runAndWait()


def txtToWav(voice, fileName, txt):
    # 替换为你的密钥、区域和端点
    subscription_key = "704e998226314ae08572550d8535814a"
    region = "eastus"

    # 配置 Speech SDK
    speech_config = SpeechConfig(subscription=subscription_key, region=region)
    speech_config.speech_synthesis_voice_name = voice
    ensure_directory_exists(file_path + "/" + "wav/")
    # 设置音频输出配置
    audio_config = audio.AudioOutputConfig(filename=file_path + "/" + "wav/" + fileName + '.wav')

    # 创建 SpeechSynthesizer，并设置语音人物
    synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    # 合成文本
    result = synthesizer.speak_text(txt)
    # 检查合成结果
    if result.reason == ResultReason.SynthesizingAudioCompleted:
        return True
    else:
        return False


def ensure_directory_exists(directory_path):
    if not os.path.exists(directory_path):
        os.makedirs(directory_path)
        print(f"目录 '{directory_path}' 不存在，已创建。")
    else:
        print(f"目录 '{directory_path}' 已存在。")


def convert_m4a_to_wav(input_file):
    # AudioSegment.converter = "D:/ffmpeg-6.0-essentials_build/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
    audio = AudioSegment.from_file(input_file, format="m4a")
    fileName = uuid.uuid4().hex
    filePath = file_path + '/' + 'wav' + '/' + fileName + "." + 'wav'
    ensure_directory_exists(file_path + '/' + 'wav')
    audio.export(filePath, format="wav")
    savaPath = fileSrc + 'wav' + '/' + fileName + "." + 'wav'
    return {'srcPath': filePath, 'url': savaPath}
    # Delete the source file
def convert_mp4_to_wav(input_file):
    # AudioSegment.converter = "D:/ffmpeg-6.0-essentials_build/ffmpeg-6.0-essentials_build/bin/ffmpeg.exe"
    audio = AudioSegment.from_file(input_file, format="mp4")
    fileName = uuid.uuid4().hex
    filePath = file_path + '/' + 'wav' + '/' + fileName + "." + 'wav'
    ensure_directory_exists(file_path + '/' + 'wav')
    audio.export(filePath, format="wav")
    savaPath = "D:/"
    return {'srcPath': filePath, 'url': savaPath}
    # Delete the source file


def get_audio_duration(file_path):
    audio = AudioSegment.from_file(file_path)
    duration_in_seconds = len(audio) / 1000.0
    # rounding to one decimal place
    return round(duration_in_seconds, 2) # 返回时长（以秒为单位）


def elevenlabs_to_wav(voice, fileName, txt):
    set_api_key("9746083e45103f6f4c85badead92db92")
    ensure_directory_exists(file_path + "/" + "wav/")

    voices = Voice(
        voice_id=voice,
    )
    save(
        audio=generate(
            text=txt,
            voice=voices,
            stream=False,
            stream_chunk_size=2048,
            latency=1

        ),
        # 设置音频输出配置
        filename=file_path + "/" + "wav/" + fileName + '.wav'
    )


async def asyncElevenlabs_to_wav(voice, fileName, txt):
    set_api_key("9746083e45103f6f4c85badead92db92")
    ensure_directory_exists(file_path + "/" + "wav/")

    voices = Voice(
        voice_id=voice,
    )
    save(
        audio=generate(
            text=txt,
            voice=voices,
            stream=False,
            stream_chunk_size=2048,
            latency=1

        ),
        # 设置音频输出配置
        filename=file_path + "/" + "wav/" + fileName + '.wav'
    )


if __name__ == '__main__':
    elevenlabs_to_wav()
