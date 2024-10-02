from uuid import uuid1
from pathlib import Path
from typing import Optional
from winrt.windows.data.xml.dom import XmlDocument
from xml.etree.ElementTree import Element, tostring, SubElement
from wtpc import APP_NAME, APP_USER_MODEL_ID, NOTIFICATION_ICON_PATH
from winreg import REG_SZ, OpenKey, SetValueEx, CreateKeyEx, QueryValueEx, HKEY_CURRENT_USER
from winrt.windows.ui.notifications import ToastNotification, ToastNotificationManager, ToastNotificationPriority

KEY_PATH = f'SOFTWARE\\Classes\\AppUserModelId\\{APP_USER_MODEL_ID}'

def is_aumid_installed() -> bool:
    try:
        with OpenKey(HKEY_CURRENT_USER, KEY_PATH) as key_handle:
            QueryValueEx(key_handle, 'DisplayName')
            return True
    except:
        return False

def install_aumid() -> None:
    with CreateKeyEx(HKEY_CURRENT_USER, KEY_PATH) as key_handle:
        SetValueEx(key_handle, 'DisplayName', 0, REG_SZ, APP_NAME)
        SetValueEx(key_handle, 'IconBackgroundColor', 0, REG_SZ, '00C0FFFF')
        SetValueEx(key_handle, 'IconUri', 0, REG_SZ, str(NOTIFICATION_ICON_PATH))

def show_notification(
        title: str,
        *,
        message: Optional[str] = None,
        image_path: Optional[Path] = None,
        priority: ToastNotificationPriority = ToastNotificationPriority.DEFAULT,
) -> Optional[str]:
    if not is_aumid_installed():
        return None

    manager = ToastNotificationManager.get_default()
    notifier = manager.create_toast_notifier(APP_USER_MODEL_ID)

    toast_xml = Element('toast', {'launch': 'default'})
    visual_xml = SubElement(toast_xml, 'visual')
    binding_xml = SubElement(visual_xml, 'binding', {'template': 'ToastGeneric'})

    title_xml = SubElement(binding_xml, 'text')
    title_xml.text = title

    if message is not None:
        message_xml = SubElement(binding_xml, 'text')
        message_xml.text = message

    if image_path is not None and image_path.exists():
        SubElement(binding_xml, 'image', {'placement': 'hero', 'src': str(image_path)})

    doc = XmlDocument()
    doc.load_xml(tostring(toast_xml, encoding='unicode'))

    id_ = f'wtpc-toast-{uuid1()}'
    toast = ToastNotification(doc)
    toast.tag = id_
    toast.priority = priority

    notifier.show(toast)

    return id_

def clear_notifications() -> None:
    manager = ToastNotificationManager.get_default()
    manager.history.clear(APP_USER_MODEL_ID)
