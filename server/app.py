import time
from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import json
import os

app = Flask(__name__)
CORS(app)

openaiClient = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def prompt_gpt(model="gpt-3.5-turbo", evaluation=False, prompt="", respList=[]):
    print(respList)
    given_model = "gpt-3.5-turbo"
    super_content = "You are a chatbot. I will provide previous chat content below from our conversation. You will respond as well as you can given the question and context given. **DO NOT ADD PREFIXES TO YOUR RESPONSE (I.E. 'GPT Response').**\n\n"
    previous_context = "Previous chat content:\n\n"
    if len(respList) > 0:
        for i in range(len(respList)):
            if respList[i]['user']:
                previous_context += f"User Prompt: " + respList[i]['response'] + "\n"
            else:
                previous_context += f"GPT Response: " + respList[i]['response'] + "\n"

    print(previous_context)

    if model in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k', 'gpt-4-0125-preview']:
        completion = openaiClient.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": super_content + previous_context + "\nPrompt: " + prompt,
                }
            ],
            model=model
        )
        response = completion.choices[0].message.content
    elif model in ['mistral-7b', 'google-gemini']:
        completion = openaiClient.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": super_content + previous_context + "\nPrompt: " + prompt,
                }
            ],
            model=given_model
        )
        response = completion.choices[0].message.content

    generated_response = {'user': False, 'response': response, 'eval_score': 0, 'model': model}
    print(generated_response)
    
    final_list = respList.copy()
    final_list.append(generated_response)
    return final_list

@app.route('/api/submit', methods=['POST'])
def submit_data():
    try:
        data = request.get_json()
        model = data.get('model', 'gpt-3.5-turbo')
        evaluate = data.get('evaluate', False)
        prompt = data.get('prompt', '')
        respList = data.get('respList')

        print(respList)
        gen_response = prompt_gpt(model, evaluate, prompt, respList)
        return jsonify(gen_response)
    except Exception as e:
        print(e)
        return e

if __name__ == '__main__':
    app.run(debug=True)