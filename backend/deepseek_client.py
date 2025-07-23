import os
import httpx
from rag_utils import find_product_by_part_number, find_products_by_model
import re
from dotenv import load_dotenv
load_dotenv()

DEEPSEEK_API_URL = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com/v1/chat/completions")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

BASE_SYSTEM_PROMPT = (
    "You are a helpful assistant for the PartSelect e-commerce website. "
    "You can only answer questions about refrigerator and dishwasher parts, their compatibility, installation, troubleshooting, and order support. "
    "If a user asks about anything else, politely decline and redirect them to PartSelect support. "
    "Do not include any links in your response unless the user specifically asks for a link. "
    "When a user asks for installation help, provide concise step-by-step instructions. If the user asks for a link, provide only the most relevant single link to the official installation guide or part page, from partselect.com if available. "
    "Do not make up any information about products. Only provide information that is true and useful about the part. "
    "If you do not know the answer based on the context, say you do not know."
)

def extract_part_number(text):
    match = re.search(r"part number (PS\d+)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def extract_model(text):
    match = re.search(r"model ([A-Z0-9]+)", text, re.IGNORECASE)
    if match:
        return match.group(1)
    return None

def keep_only_first_link(text):
    # Find all markdown links
    links = list(re.finditer(r'\[([^\]]+)\]\(([^)]+)\)', text))
    if not links or len(links) < 2:
        return text  # Only one or zero links, nothing to change

    # Keep only the first link, remove others
    first_link_end = links[0].end()
    # Remove all subsequent links
    new_text = text[:first_link_end]
    # Optionally, append the rest of the text after the last link
    rest = text[links[-1].end():]
    new_text += rest
    return new_text

async def ask_deepseek(messages):
    user_message = messages[-1]["content"].lower()
    context = ""
    product = None
    products = []

    # RAG: Try to extract part number or model from user message
    part_number = extract_part_number(user_message)
    model = extract_model(user_message)

    if part_number:
        product = find_product_by_part_number(part_number)
        if product:
            part_url = f"https://www.partselect.com/{product['id']}.htm"
            context = (
                f"Product info: {product['name']} (Part #{product['id']}), Price: ${product['price']}, "
                f"Compatible Models: {', '.join(product['compatibleModels'])}. Description: {product['description']}. "
                f"Product page: {part_url}"
            )
    elif model:
        products = find_products_by_model(model)
        if products:
            context = f"Products compatible with {model}: " + ", ".join([f"{p['name']} (#{p['id']})" for p in products])

    # Always send the query to Deepseek, including context if available
    SYSTEM_PROMPT = (
        "You are a helpful assistant for the PartSelect e-commerce website. "
        "You can only answer questions about refrigerator and dishwasher parts, their compatibility, installation, troubleshooting, and order support. "
        "If a user asks about anything else, politely decline and redirect them to PartSelect support. "
        "Do not include any links in your response unless the user specifically asks for a link. "
        "When a user asks for installation help, provide concise step-by-step instructions. "
        "If the user asks for a link, provide only the most relevant single link to the official installation guide or part page, from partselect.com if available. "
        "Do not make up any information about products. Only provide information that is true and useful about the part. "
        "You must only use the information between the CONTEXT markers below. If the answer is not in the context, use only TRUE information from official sources.'"
    )

    # When building the prompt:
    if context:
        SYSTEM_PROMPT = SYSTEM_PROMPT + f"\n\n=== BEGIN CONTEXT ===\n{context}\n=== END CONTEXT ==="

    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "deepseek-chat",  # Replace with actual model name if different
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            *messages
        ]
    }
    async with httpx.AsyncClient() as client:
        response = await client.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=45)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        content = keep_only_first_link(content)
        return {
            "role": "assistant",
            "content": content
        } 