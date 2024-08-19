import mimetypes

import uuid

from soulmate_server.conf.systemConf import AUDIO_MIME_TYPE_MAPPING, file_path, fileSrc
from soulmate_server.utils.mp3 import ensure_directory_exists


def get_file_extension(file_format: str) -> str:
    # ���Դ��ֶ�ӳ���л�ȡ��չ��
    extension = AUDIO_MIME_TYPE_MAPPING.get(file_format)
    if extension:
        return extension

    # ����Ҳ���ӳ�䣬��ʹ�� mimetypes
    return mimetypes.guess_extension(file_format, strict=False) or ".bin"


# �����ļ� ����path ��ָҪ�����ĸ��ļ����� Ŀǰ��֧�ַ��ڸ�Ŀ¼ ���÷���
def upload_file(file, path, srcType: int = 0):
    fileName = uuid.uuid4().hex
    original_filename = file.filename
    # ��ȡԭʼ��׺
    original_filename_suffix = original_filename.split('.')[-1]
    # ��ȡ�ļ�·��

    filePath = file_path + '/' + path + '/' + fileName + "." + original_filename_suffix
    ensure_directory_exists(file_path + '/' + path)
    with open(filePath, "wb") as f:
        f.write(file.file.read())
    savaPath = fileSrc + path + '/' + fileName + "." + original_filename_suffix
    if srcType == 0:

        return savaPath
    else:
        return {'srcPath': filePath, 'url': savaPath}
