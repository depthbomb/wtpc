from base64 import b64encode
from typing import cast, Optional
from datetime import datetime, timedelta
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest, QNetworkAccessManager
from wtpc.settings import app_settings, user_settings, AppSettingsKeys, UserSettingsKeys
from PySide6.QtCore import Slot, QUrl, Signal, QTimer, QObject, QByteArray, QJsonDocument

OAUTH_URL = QUrl('https://oauth.battle.net/token')

TIMER_INTERVAL = 2_000

class PriceCheckWorker(QObject):
    error = Signal(str)
    price_updated = Signal(int, int)

    def __init__(self):
        super().__init__()

        self.network_manager = QNetworkAccessManager()
        self.network_manager.finished.connect(self._on_network_manager_finished)

        self.timer = QTimer()
        self.timer.setInterval(TIMER_INTERVAL)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self._on_timer_timeout)
        self.timer.start()

    #region Signal Handlers
    @Slot(QNetworkReply)
    def _on_network_manager_finished(self, reply: QNetworkReply):
        reply.deleteLater()

        url = reply.url()
        status_code = int(reply.attribute(QNetworkRequest.Attribute.HttpStatusCodeAttribute))
        if status_code == 200:
            json = QJsonDocument.fromJson(reply.readAll()).object()
            if url == OAUTH_URL:
                access_token = cast(str, json['access_token'])
                expires_in = cast(int, json['expires_in'])

                app_settings.setValue(AppSettingsKeys.ACCESS_TOKEN, access_token)
                app_settings.setValue(AppSettingsKeys.ACCESS_TOKEN_EXPIRES, datetime.now() + timedelta(seconds=expires_in))

                self.check_price()
            else:
                last_updated_timestamp = cast(int, json['last_updated_timestamp']) / 1000
                price = cast(int, json['price']) // 10_000

                self.price_updated.emit(price, last_updated_timestamp)
        elif status_code == 401:
            self._get_access_token()
        else:
            print(status_code)
            self.error.emit(reply.errorString())

    @Slot()
    def _on_timer_timeout(self):
        self.check_price()
    #endregion

    def check_price(self):
        now = datetime.now()
        access_token = cast(Optional[str], app_settings.value(AppSettingsKeys.ACCESS_TOKEN, None))
        access_token_expires = cast(Optional[datetime], app_settings.value(AppSettingsKeys.ACCESS_TOKEN_EXPIRES, None))
        is_token_expired = access_token_expires is None or access_token_expires < now

        if access_token is None or is_token_expired:
            self._get_access_token()
        else:
            self._get_token_price()

    def _get_access_token(self):
        client_id = user_settings.value(UserSettingsKeys.CLIENT_ID)
        client_secret = user_settings.value(UserSettingsKeys.CLIENT_SECRET)
        auth = b64encode(bytes(f'{client_id}:{client_secret}'.encode('utf-8'))).decode('utf-8')

        req = QNetworkRequest(OAUTH_URL)
        req.setHeader(QNetworkRequest.KnownHeaders.ContentTypeHeader, 'application/x-www-form-urlencoded')
        req.setRawHeader(b'Authorization', f'Basic {auth}'.encode('utf-8'))

        form = QByteArray()
        form.append(b'grant_type=client_credentials')

        self.network_manager.post(req, form)

    def _get_token_price(self):
        access_token = app_settings.value(AppSettingsKeys.ACCESS_TOKEN, None)
        region = user_settings.value(UserSettingsKeys.REGION, None)

        host: QUrl
        match region:
            case 'dynamic-eu':
                host = QUrl('https://eu.api.blizzard.com')
            case 'dynamic-kr':
                host = QUrl('https://kr.api.blizzard.com')
            case 'dynamic-tw':
                host = QUrl('https://tw.api.blizzard.com')
            case _:
                host = QUrl('https://us.api.blizzard.com')

        host.setPath('/data/wow/token/index')

        req = QNetworkRequest(host)
        req.setRawHeader(b'Battlenet-Namespace', f'{region}'.encode('utf-8'))
        req.setRawHeader(b'Authorization', f'Bearer {access_token}'.encode('utf-8'))

        self.network_manager.get(req)
