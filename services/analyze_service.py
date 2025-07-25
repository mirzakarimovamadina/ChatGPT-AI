import httpx
from config import API_TOKEN

async def analyze_text(text: str) -> str:
    prompt = f"""Matnni quyidagi toifalardan biriga ajrat:
    
1. ❓Savol
2. 💭Fikr
3. 😂Kulgili
4. ⚠️Noto‘g‘ri yoki tushunarsiz (toxirlik)

Faqat mos keladigan belgini yubor:
Matn: "{text}"
Javob:
"""

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    json_data = {
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=json_data
        )
        result = response.json()
        answer = result["choices"][0]["message"]["content"].strip()
        return answer
