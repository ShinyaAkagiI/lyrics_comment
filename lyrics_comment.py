from pytube import YouTube
from spleeter.separator import Separator
import whisper
import googleapiclient.discovery
import re
import google_auth_oauthlib.flow

urls = ["https://www.youtube.com/watch?v=ycDHPbYJcpA"] # 動画のURLリスト
api_service_name = "youtube"
api_version = "v3"
channelid = "UCKH6taytLBMurusP0nHZs9A" # コメント投稿するアカウントのチャンネルID
dougaid = re.compile("\?v=([^&]+)")
client_secrets_file = "client_secrets.json" # OAUTH認証用のJSONファイル
scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
credentials = flow.run_console() # 注意：本来ここで1回のみ認証して欲しいが、なぜか処理の途中で2回目の認証が求められる
youtube = googleapiclient.discovery.build(api_service_name, api_version, credentials=credentials)


def download_youtube(url, output_fname="output.mp4"):
  # urlの動画を保存
  stream = YouTube(url).streams.filter(file_extension="mp4").first()
  stream.download(filename=output_fname)


def separate_audio(fname="output.mp4"):
  # ボーカルとそれ以外に分離する(2音源)
  separator = Separator("spleeter:2stems")

  # ./output/vocals.wavと./output/accompaniment.wavを作成
  separator.separate_to_file(fname, ".")


def speech_to_text():
  # modelをtiny, base, small, medium, largeから選択
  # 右のmodelほど精度は高いが処理時間が長くなる
  model = whisper.load_model("medium")
  result = model.transcribe("output/vocals.wav", language="ja")
  return result["text"]


def comment_youtube(text, url):
  # 動画にコメント済みの場合は新規投稿しない
  yid = dougaid.findall(url)[0]
  request = youtube.commentThreads().list(part="snippet", videoId=yid)
  response = request.execute()
  cids = set()
  try:
    for item in response["items"]:
      cids.add(item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"]["value"])
  except:
    pass

  if channelid in cids:
    print("コメント済みのため、コメントを投稿しませんでした。")
    return 0

  # OAUTHで選択したチャンネルを設定しないと、ineligibleAccountエラーが発生することがある
  request = youtube.commentThreads().insert(
    part="snippet",
    body={
      "snippet": {
        "channelId": channelid,
        "videoId": yid,
        "topLevelComment": {
          "snippet": {
            "textOriginal": text
          }
        }
      }
    }
  )
  response = request.execute()


def lyrics_comment(url):
  print("歌詞の抽出開始：（0/5）")

  print("動画のダウンロード開始：（1/5）")
  download_youtube(url)

  print("動画のボーカル部分の抽出開始：（2/5）")
  separate_audio()

  print("ボーカル部分の文字起こし開始：（3/5）")
  text = speech_to_text()
  text = text + "\n\n※本テキストは文字起こしツールwhisperを使用して自動生成しています。\n※解析誤りもそのまま表示しているため、参考程度としてご確認ください。"
  print(text)

  print("Youtubeへのコメント投稿開始：（4/5）")
  comment_youtube(text, url)

  print("歌詞のコメント投稿完了済み（5/5）")


if __name__=="__main__":
  for i, url in enumerate(urls):
    print("---------------------------")
    print("{}/{}番目の処理開始".format(i+1, len(urls)))
    print("---------------------------")
    lyrics_comment(url)
