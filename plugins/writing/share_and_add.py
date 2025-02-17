import re
import time
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
from pyrogram import Client, filters
from pyrogram.enums import ChatAction
from data import Database
from sub_task import kv


owners = kv["owners"]


def parse_url(url):
    parts = urlparse(url)
    query = parse_qs(parts.query)
    id_value = query.get("token", [None])[0]
    new_query = {"token": id_value} if id_value is not None else {}
    new_url = urlunparse(
        (
            parts.scheme,
            parts.netloc,
            parts.path,
            parts.params,
            urlencode(new_query, doseq=True),
            parts.fragment,
        )
    )
    return new_url


@Client.on_message(filters.command("add"))
def add_url(c, m):
    db = Database()
    m.reply_chat_action(ChatAction.TYPING)
    user_id = m.from_user.id
    if m.from_user.id in owners:
        note_name = "v2ray"
    else:
        note_name = "default"
    text = m.text
    if m.reply_to_message:
        text = m.reply_to_message.text
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    if note_name == "v2ray":
        if user_id not in owners:
            m.reply("**You don't have permission to access this note**", quote=True)
            return
    if not urls:
        err = m.reply_text("Vui lòng cung cấp URL")
        time.sleep(10)
        c.delete_messages(m.chat.id, err.id)
        m.delete()
        return
    li = 0
    note = db.get_note(note_name)
    if note:
        if user_id not in [note.auth_id, *owners]:
            m.reply("**You don't have permission to access this note**", quote=True)
            return
    else:
        db.add_note(note_name, user_id)
        note = db.get_note(note_name)
    note_urls = note.urls.split("\n")
    for url in urls:
        if "api/v1/client" in url:
            url = parse_url(url)
        if url not in note_urls:
            note_urls.append(url)
            li += 1
        else:
            print("Existing")
    note.urls = "\n".join(note_urls)
    db.update_note(note)
    if li != len(urls):
        x = len(urls) - li
        temp = m.reply(f"{x} URL trùng lặp sẽ không được thêm lại")
        time.sleep(5)
        c.delete_messages(m.chat.id, temp.id)
    done = m.reply_text(f"Đã thêm {li} URL")
    time.sleep(10)
    c.delete_messages(m.chat.id, done.id)
    m.delete()


@Client.on_message(filters.command("share"))
def share_url(c, m):
    db = Database()
    m.reply_chat_action(ChatAction.TYPING)
    text = m.text
    if m.reply_to_message:
        text = m.reply_to_message.text
    urls = re.findall(
        r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
        text,
    )
    if not urls:
        err = m.reply_text("Vui lòng cung cấp URL")
        time.sleep(10)
        c.delete_messages(m.chat.id, err.id)
        return
    li = 0
    for url in urls:
        if "api/v1/client" in url:
            url = parse_url(url)
            note_name = "default"
        else:
            note_name = "misc"
        note = db.get_note(note_name)
        if not note:
            db.add_note(note_name, 0)
            note = db.get_note(note_name)
        note_urls = note.urls.split("\n")
        if url not in note_urls:
            note_urls.append(url)
            li += 1
        else:
            print("Existing")
        note.urls = "\n".join(note_urls)
        db.update_note(note)
    if li != len(urls):
        x = len(urls) - li
        temp = m.reply(f"{x} URL trùng lặp sẽ không được thêm lại")
        time.sleep(10)
        c.delete_messages(m.chat.id, temp.id)
    done = m.reply_text(f"Đã thêm {li} URL")
    time.sleep(10)
    done.delete()
