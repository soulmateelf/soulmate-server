import mimetypes

import uuid

from soulmate_server.conf.systemConf import AUDIO_MIME_TYPE_MAPPING, file_path, fileSrc
from soulmate_server.utils.mp3 import ensure_directory_exists


def get_file_extension(file_format: str) -> str:
    # 尝试从手动映射中获取扩展名
    extension = AUDIO_MIME_TYPE_MAPPING.get(file_format)
    if extension:
        return extension

    # 如果找不到映射，则使用 mimetypes
    return mimetypes.guess_extension(file_format, strict=False) or ".bin"


# 保存文件 参数path 是指要放在哪个文件夹下 目前不支持放在根目录 做好分类
def upload_file(file, path, srcType: int = 0):
    fileName = uuid.uuid4().hex
    original_filename = file.filename
    # 获取原始后缀
    original_filename_suffix = original_filename.split('.')[-1]
    # 获取文件路径

    filePath = file_path + '/' + path + '/' + fileName + "." + original_filename_suffix
    ensure_directory_exists(file_path + '/' + path)
    with open(filePath, "wb") as f:
        f.write(file.file.read())
    savaPath = fileSrc + path + '/' + fileName + "." + original_filename_suffix
    if srcType == 0:

        return savaPath
    else:
        return {'srcPath': filePath, 'url': savaPath}
