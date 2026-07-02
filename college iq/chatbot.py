import requests

MODEL_NAME = "phi3"

def get_reply(message):

    try:

        response = requests.post(

            "http://localhost:11434/api/generate",

            json={
                "model": MODEL_NAME,
                "prompt": message,
                "stream": False
            },

            timeout=120
        )

        data = response.json()

        return data["response"]

    except Exception as e:

        return f"Error: {str(e)}"