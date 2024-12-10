import os
import openai
import requests
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Set your API keys here
# NEWS_API_KEY = 'your_news_api-key'
OPENAI_API_KEY = 'your-openai-api-key'
DALL_E_API_KEY = 'your-dall-e-api-key'
IMGFLIP_USERNAME = 'your-imgflip-username'
IMGFLIP_PASSWORD = 'your-imgflip-password'

NEWS_API_KEY = '97442c46164a4cf9bbfd6a9b0ce74658'

openai.api_key = OPENAI_API_KEY


# Add CORS middleware to allow requests from React frontend
origins = [
    "http://localhost:5173",  # React app's URL
    "https://mind-matrix-ui.vercel.app/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows requests from React
    allow_credentials=True,
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)

# Pydantic models for input and output
class TextGenerationRequest(BaseModel):
    prompt: str
    #tone: str

class ImageGenerationRequest(BaseModel):
    description: str

class MemeGenerationRequest(BaseModel):
    templateId: int
    topText: str
    bottomText: str

class NewsRequest(BaseModel):
    query: str

class NewsArticle(BaseModel):
    title: str
    description: str
    url: str

class TextGenerationResponse(BaseModel):
    generatedText: str

class ImageGenerationResponse(BaseModel):
    imageUrl: str

class MemeGenerationResponse(BaseModel):
    memeUrl: str

class NewsResponse(BaseModel):
    articles: List[NewsArticle]


# Helper function to fetch news articles
def fetch_news(query: str):
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={NEWS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    return data['articles']

@app.get("/")
async def read_root():
    return {"message": "Welcome to MindMatrix API"}

# Route to generate text content using GPT-4
@app.post("/generateText", response_model=TextGenerationResponse)
async def generate_text(request: TextGenerationRequest):
    prompt = request.prompt
    tone = request.tone
    
    # Generate text using OpenAI API
    response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Generate a {tone} post about: {prompt}",
        max_tokens=150
    )
    return TextGenerationResponse(generatedText=response.choices[0].text.strip())


# Route to generate image using DALL·E API
@app.post("/generateImage", response_model=ImageGenerationResponse)
async def generate_image(request: ImageGenerationRequest):
    description = request.description
    
    # Generate image using DALL·E
    response = requests.post(
        'https://api.openai.com/v1/images/generations',
        json={
            "prompt": description,
            "n": 1,
            "size": "512x512"
        },
        headers={
            'Authorization': f'Bearer {DALL_E_API_KEY}'
        }
    )
    image_url = response.json()['data'][0]['url']
    return ImageGenerationResponse(imageUrl=image_url)


# Route to generate meme using Imgflip API
@app.post("/generateMeme", response_model=MemeGenerationResponse)
async def generate_meme(request: MemeGenerationRequest):
    template_id = request.templateId
    top_text = request.topText
    bottom_text = request.bottomText
    
    # Generate meme using Imgflip API
    response = requests.post(
        'https://api.imgflip.com/caption_image',
        data={
            'template_id': template_id,
            'text0': top_text,
            'text1': bottom_text,
            'username': IMGFLIP_USERNAME,
            'password': IMGFLIP_PASSWORD
        }
    )
    meme_url = response.json()['data']['url']
    return MemeGenerationResponse(memeUrl=meme_url)


# Route to fetch news articles
@app.post("/fetchNews", response_model=NewsResponse)
async def fetch_news_route(request: NewsRequest):
    query = request.query
    
    # Fetch news articles using News API
    articles = fetch_news(query)
    news_articles = [NewsArticle(title=article['title'], description=article['description'], url=article['url']) for article in articles]
    return NewsResponse(articles=news_articles)


# Run the app
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port= 8000, reload = True )
