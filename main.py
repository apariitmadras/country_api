from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests

app = FastAPI()

# Enable CORS for all origins (allow from any frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

@app.get("/api/outline")
def get_country_outline(country: str = Query(..., description="Country name")):
    country_formatted = country.strip().replace(" ", "_")
    url = f"https://en.wikipedia.org/wiki/{country_formatted}"

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        raise HTTPException(status_code=404, detail=f"Wikipedia page not found for '{country}'.")

    soup = BeautifulSoup(response.text, "html.parser")
    headings = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])

    if not headings:
        raise HTTPException(status_code=404, detail="No headings found on Wikipedia page.")

    markdown = ["## Contents", f"# {country.strip()}"]
    for heading in headings:
        level = int(heading.name[1])
        text = heading.get_text().strip()
        markdown.append(f"{'#' * level} {text}")

    return {"country": country, "outline": "\n\n".join(markdown)}
