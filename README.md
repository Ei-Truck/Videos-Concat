# 🎬 API Concatenadora de Vídeos

Esta API permite **baixar vídeos diretamente de URLs do Amazon S3**, **concatená-los na ordem enviada** e **enviar o resultado novamente para um bucket S3**.  

## 🚀 Tecnologias Utilizadas

| Tecnologia | Função |
|-----------|--------|
| **Python 3** | Linguagem principal |
| **FastAPI** | Framework para a API |
| **MoviePy** | Manipulação e concatenação dos vídeos |
| **Boto3** | Comunicação com AWS S3 |
| **Docker** | Containerização da aplicação |

## 📦 Estrutura do Projeto

**Videos-Concat/**
main.py -> Código principal da API
requirements.txt -> Dependências
Dockerfile -> Container da aplicação
.env.example -> Exemplo de variáveis de ambiente
.gitignore

## 🏃 Como Executar o Projeto

### 1️⃣ Criar a imagem Docker

```bash
docker build -t videos-concat .
````
### 2️⃣ Rodar o container
```bash
docker run -p 8000:8000 --env-file .env videos-concat
```

## Documentação Swagger ficara disponivel em
http://localhost:8000/docs

## Como usar

**Exemplo de request**
```json
{
  [
    "https://bucket.s3.amazonaws.com/video1.mp4",
    "https://bucket.s3.amazonaws.com/video2.mp4"
  ]
}
```

**Exemplo de resposta**
```json
{
  "message": "Vídeo concatenado com sucesso!",
  "output_url": "https://bucket.s3.amazonaws.com/resultado/video_final.mp4"
}
```

## 🔧 Variáveis de Ambiente

**Crie um arquivo .env com as seguintes variáveis:**
```env
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1 
S3_BUCKET_NAME=nome-do-seu-bucket
```

**Você pode se basear no arquivo .env.example incluído no projeto.**

## 📝 Observações

**A ordem dos vídeos no array `urls` define a ordem da concatenação.**

**Certifique-se de que os vídeos têm formatos compatíveis `(ex: mp4)` e codecs iguais para evitar erros.**

**Para arquivos muito grandes, recomenda-se otimizar o processamento ou aumentar os recursos do container.**
