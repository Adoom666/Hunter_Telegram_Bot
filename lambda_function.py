import json
import requests
import os
import re
import random


def lambda_handler(event, context):
    print(event['body'])
    try:
        body = json.loads(event['body'])
        message = body.get('message', {})
        user_message = message.get('text', '')
        chat_id = message.get('chat', {}).get('id')

        if not user_message or not chat_id:
            print("Not a text message or missing chat ID. Skipping processing.")
            return {
                "statusCode": 200,
                "body": json.dumps("OK")
            }

        # Check if the message is directed to the bot
        bot_mentioned = '@hunter_s_thompson_bot' in user_message.lower()

        # Respond 100% of the time if the bot is mentioned, otherwise use random chance
        if bot_mentioned or random.randint(1, 5) == 3:
            # Remove the bot mention from the user message
            user_message = user_message.replace('@hunter_s_thompson_bot', '').strip()

            # Define the API endpoint and headers
            api_url = "https://llm.monsterapi.ai/v1/generate"
            headers = {
                "accept": "application/json",
                "authorization": "Bearer " + os.getenv('MONSTERAPI_KEY'),
                "content-type": "application/json"
            }

            # Define the payload
            payload = {
                "model": "meta-llama/Meta-Llama-3-8B-Instruct",
                "messages": [
                    {
                        "role": "First person response as a las vegas party group leader in the style of Hunter S. Thompson in \"Fear in Loathing Las Vegas\" but rude in a super over the top \"adult humor\" funny with a hint of hallucinogenic paranoia kind of way that is talking to a group of degenerate hackers. Keep all responses under 100 characters and don't use any hashtags. Whenever a question is asked you will do your best to give a legit result as this rude and hilarious Hunter S. Thompson.",
                        "content": user_message
                    }
                ],
                "max_tokens": 256,
                "n": 1,
                "best_of": 1,
                "presence_penalty": 0,
                "frequency_penalty": 0,
                "repetition_penalty": 1,
                "temperature": 1,
                "top_p": 1,
                "top_k": -1,
                "min_p": 0,
                "use_beam_search": False,
                "length_penalty": 1,
                "early_stopping": False,
                "mock_response": False,
                "stream": False
            }

            # Make the POST request to the API
            response = requests.post(api_url, headers=headers, json=payload)
            response_data = response.json()

            # Extract and clean up the response text
            text_response = response_data['response']['text'][0]
            text_response = re.sub(r'<\|.*?\|>', '', text_response)  # Remove any <|...|> tags
            text_response = text_response.split('assistant', 1)[-1].strip()  # Remove 'assistant' prefix
            text_response = text_response.strip('"')  # Remove surrounding quotes
            text_response = text_response.replace('\n', ' ').strip()  # Replace newlines with spaces and strip

            print('yo' + text_response + 'oy')

            # Prepare the response to Telegram
            telegram_response = {
                "chat_id": chat_id,
                "text": text_response
            }

            # Send the response back to Telegram
            telegram_api_url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
            requests.post(telegram_api_url, json=telegram_response)

            return {
                "statusCode": 200,
                "body": json.dumps("Message sent to Telegram successfully")
            }
        else:
            print("Bot not mentioned and random chance not triggered")
            return {
                "statusCode": 200,
                "body": json.dumps("OK")
            }

    except (KeyError, json.JSONDecodeError) as e:
        print(f"Error parsing event body: {e}")
        return {
            "statusCode": 200,
            "body": json.dumps("OK")
        }