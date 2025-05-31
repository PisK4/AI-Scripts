curl --request POST \
  --url https://api.siliconflow.cn/v1/uploads/audio/voice \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: multipart/form-data' \
  --form 'audio=data:audio/mpeg;base64,aGVsbG93b3JsZA==' \
  --form model=FunAudioLLM/CosyVoice2-0.5B \
  --form customName=your-voice-name \
  --form 'text=在一无所知中, 梦里的一天结束了，一个新的轮回便会开始'