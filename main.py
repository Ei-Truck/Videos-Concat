from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import boto3
import tempfile
import os
import uuid
from datetime import datetime
from moviepy import VideoFileClip, CompositeVideoClip
from urllib.parse import urlparse

app = FastAPI(
    title="API Concatenador de Vídeos",
    description="Recebe URLs de vídeos da AWS S3, concatena e envia para o S3.",
    version="1.0.0"
)

AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_BUCKET = os.getenv("AWS_BUCKET_NAME")
AWS_REGION = os.getenv("AWS_REGION")

s3 = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    # Se você tiver um domínio de produção, adicione-o aqui também
    # "https://seudominiofrontend.com"
]
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,              # Lista de origens permitidas
    allow_credentials=True,             # Permite cookies/credenciais
    allow_methods=["*"],                # Permite todos os métodos (GET, POST, etc.)
    allow_headers=["*"],                # Permite todos os cabeçalhos
)

@app.get("/")
async def root():
    return {"message": "API online!"}

@app.post("/concatenar")
async def concatenar_videos(id_motorista: int, videos: list[str]):
    arquivos_temp = []
    clips = []
    output_path = None

    try:
        for url in videos:
            parsed = urlparse(url)
            key_s3 = parsed.path.lstrip('/')
            print(f"Key S3 detectada: {key_s3}")

            with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_file:
                s3.download_fileobj(AWS_BUCKET, key_s3, tmp_file)
                arquivos_temp.append(tmp_file.name)

        tempo_atual = 0
        for caminho in arquivos_temp:
            clip = VideoFileClip(caminho)
            clip = clip.with_start(tempo_atual)
            tempo_atual += clip.duration
            clips.append(clip)

        video_final = CompositeVideoClip(clips)

        output_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        output_path = output_temp.name
        output_temp.close()

        video_final.write_videofile(output_path, codec="libx264", audio_codec="aac")

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = uuid.uuid4().hex[:6]
        nome_saida = f"video_final_{timestamp}_{unique_id}.mp4"

        with open(output_path, "rb") as f:
            caminho_s3 = f"concatenadas/{id_motorista}/{nome_saida}"
            s3.upload_fileobj(f, AWS_BUCKET, caminho_s3)


        url_final = f"https://{AWS_BUCKET}.s3.{AWS_REGION}.amazonaws.com/concatenadas/{id_motorista}/{nome_saida}"

        return {"status": "ok", "video_final_url": url_final}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        for clip in clips:
            try:
                clip.reader.close()
                if clip.audio:
                    clip.audio.reader.close_proc()
            except:
                pass

        for caminho in arquivos_temp:
            try:
                os.remove(caminho)
            except:
                pass

        if output_path and os.path.exists(output_path):
            os.remove(output_path)
