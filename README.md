# 概要
  
Youtubeの動画を解析し、歌詞をコメント欄に投稿するスクリプトです。  
Youtubeの動画取得には、pytubeモジュールを、  
ボーカル部分の音源分離には、spleeterモジュールを、  
音声の文字起こしには、whisperモジュールを、  
Youtubeのコメント投稿には、Youtube CommentThreads APIを使用しています。  
  
# 事前準備
  
事前に以下を実施する必要があります。  
- pytube, spleeter, whisper, google-api-python-client, google-auth-oauthlib, google-auth-httplib2のインストール
- Youtubeチャンネルの作成、チャンネルIDの確認
- Google Cloud Consoleにおいて、Youtube Data APIの有効化
- Google Cloud Consoleにおいて、OAuth2.0クライアントの登録、client_secrets.jsonのダウンロード
