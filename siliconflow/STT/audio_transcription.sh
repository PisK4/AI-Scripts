curl --request POST \
  --url https://api.siliconflow.cn/v1/audio/transcriptions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: multipart/form-data' \
  --form model=FunAudioLLM/SenseVoiceSmall