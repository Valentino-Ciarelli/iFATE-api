import PyPDF2
import requests
import os

openai_api_key = os.environ.get("OPENAI_KEY")

openai_url = "https://api.openai.com/v1/chat/completions"

def chunk_text(text, chunk_size=4000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def GetOpenAIResponse(Prompt, Info):
    headers = {
        "Authorization": f"Bearer {openai_api_key}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "gpt-3.5-turbo-16k",
        "messages": [
            {"role": "system", "content": f"You are a PDF reader. Please summarize the provided content in less then 50 words. {Info}"},
            {"role": "user", "content": Prompt}
        ],
        "max_tokens": 1500,
        "temperature": .7
    }

    response = requests.post(openai_url, headers=headers, json=data)
    response.raise_for_status()
    response_data = response.json()
    if 'choices' in response_data and response_data['choices']:
        return response_data['choices'][0]['message']['content'].strip()
    else:
        return "No valid response received from the OpenAI API."

with open("test.pdf", "rb") as pdf_file:
    read_pdf = PyPDF2.PdfReader(pdf_file)
    all_text = ""
    for page_num in range(len(read_pdf.pages)):
        page = read_pdf.pages[page_num]
        page_content = page.extract_text()
        all_text += page_content

chunks = chunk_text(all_text, chunk_size=16000)

summaries = [GetOpenAIResponse("Summarise this content:", chunk) for chunk in chunks]

final_summary = "\n".join(summaries)
print(final_summary)
