import obspython as obs

from twitchAPI.twitch import Twitch
from twitchAPI.helper import first
import asyncio

import os
from dotenv import load_dotenv

# .envファイルの内容を読込み
load_dotenv()

# https://dev.twitch.tv/　でアプリケーション登録して取得する。
CLIENT_ID =  os.getenv("CLIENT_ID")
CLIENT_SECRET =  os.getenv("CLIENT_SECRET")

# デバッグ情報の表示
print("CLIENT_ID:", CLIENT_ID)
print("CLIENT_SECRET:", CLIENT_SECRET)

target_user = ""
text_name = ""

def script_description():
    return "ボタン押下で、指定したtwitchアカウントの配信時のタイトルとゲームを取得してテキストに反映させるスクリプト。"

def script_properties():
    props = obs.obs_properties_create()

    # 対象のユーザ名
    obs.obs_properties_add_text(props, "target_user", "Target User",obs.OBS_TEXT_DEFAULT)

    # テキストソース
    text_properties = obs.obs_properties_add_list(props, "text", "Text Source", obs.OBS_COMBO_TYPE_LIST, obs.OBS_COMBO_FORMAT_STRING)

    sources = obs.obs_enum_sources()
    for source in sources:
        source_id = obs.obs_source_get_unversioned_id(source)
        if source_id == "text_gdiplus":
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(text_properties, name, name)

    obs.source_list_release(sources)

    # ボタン
    obs.obs_properties_add_button(props, "get_twtich", "Get Twtich", on_button_clicked)

    return props

def script_update(settings):
    global target_user, text_name
    
    target_user = obs.obs_data_get_string(settings, "target_user")
    text_name = obs.obs_data_get_string(settings, "text")

def on_button_clicked(props, prop):
    print("Button clicked!")

    # 配信情報を取得
    print("target_user:", target_user)
    game_name, stream_title = asyncio.run(get_twitch_info(target_user, CLIENT_ID, CLIENT_SECRET))

    # テキストソースに反映させる文字列
    global show_text
    show_text = "[{0}] {1}".format(game_name, stream_title)
    print("show_text:", show_text)

    # テキストソースの取得
    text_source = obs.obs_get_source_by_name(text_name)

    # テキストソースに文字列を反映
    settings = obs.obs_data_create()
    obs.obs_data_set_string(settings, "text", show_text)
    obs.obs_source_update(text_source, settings)

    # テキストソースのリリース
    obs.obs_source_release(text_source)

async def get_twitch_info(target_user, client_id, client_secret):
    try:
        twitch = await Twitch(client_id, client_secret)

        user = await first(twitch.get_users(logins=target_user))
        print(user.id)

        stream = await first(twitch.get_streams(user_id=user.id))
        print(stream.game_name)
        print(stream.title)

        await twitch.close()

        return stream.game_name, stream.title
    
    except Exception as e:
        print("An error occurred:", e)
        return "error", "error"

def script_load(settings):
    print("Script loaded")

def script_unload():
    print("Script unloaded")    