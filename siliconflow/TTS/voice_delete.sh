curl --request POST \
  --url https://api.siliconflow.cn/v1/audio/voice/deletions \
  --header 'Authorization: Bearer <token>' \
  --header 'Content-Type: application/json' \
  --data '{
  "uri": "speech:your-voice-name:xxx:xxxx"
}'