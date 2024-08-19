from soulmate_server.conf.dataConf import environment

SALT = 'soulmate@2023'

headers = {
    'typ': 'jwt',
    'alg': 'HS256'
}
develop = '54.177.205.15'
production = 'neveraloneagain.app'
fileSrcs = {
    "develop": "http://" + develop + "/api/static/", "production": "https://" + production + "/api/static/"
}

developGoogleRollBack = "54.177.205.15/api/androidPurchaseNotification"
# �ֶ�ӳ����Ƶ MIME ���͵���չ��
AUDIO_MIME_TYPE_MAPPING = {
    "audio/wave": ".wav",
    # ��������������Ƶ���͵�ӳ��
}
file_path = "/soulmateServer/soulmate_server/data"

fileSrc = fileSrcs[environment]
# "http://54.177.205.15/api/static/"
