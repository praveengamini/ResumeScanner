import os
import google.generativeai as genai

genai.configure(api_key="AIzaSyBRmEv6qytadNRmZ9WwVuREzs2BxWuc38A")

print("📋 Listing available Gemini models:\n")
for model in genai.list_models():
    print(model.name)
