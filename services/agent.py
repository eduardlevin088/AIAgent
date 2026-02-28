from openai import OpenAI
from config import GPT_KEY, GPT_MODEL
from config import AGENT_PROMPT_MAIN_PATH
from config import KZ_UTC
from .miscellaneous import current_time_utc_offset
import json

with open(AGENT_PROMPT_MAIN_PATH, "r", encoding="utf-8") as f:
    agent_prompt_main = f.read()

client = OpenAI(api_key=GPT_KEY)

# 1. Define a list of callable tools for the model
tools = [
    {
        "type": "function",
        "name": "send_contact_details",
        "description": "Send FULLY COLLECTED repair request to manager ONLY after all required fields are known.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "phone": {"type": "string"},
                "city": {"type": "string"},
                "product_type": {"type": "string"},
                "model": {"type": "string"},
                "problem": {"type": "string"}
            },
            "required": ["name", "phone", "city", "product_type", "problem"]
        },
    },
]


def send_contact_details(data: dict) -> tuple[str, dict]:
    print(f"\n\n\n\n\n\n\n\nCOLLECTED DATA: {data}\n\n\n\n\n\n\n\n\n\n\n\n")
    return "Контактные данные отправлены.", data


def generate_response(message: str, conversation: str) -> tuple[str]:

    data_to_send = None
    current_time = current_time_utc_offset(KZ_UTC)

    instructions = f"{agent_prompt_main}\n\nCurrent time is {current_time}"
    input_list = [{"role": "user", "content": message}]

    response = client.responses.create(
        model=GPT_MODEL,
        tools=tools,
        input=input_list,
        conversation=conversation,
        instructions=instructions,
    )

    # Save function call outputs for subsequent requests
    # input_list += response.output

    

    for item in response.output:
        if item.type == "function_call":
            if item.name == "send_contact_details":
                # 3. Execute the function logic for get_horoscope
                args = json.loads(item.arguments)
                func_response, data_to_send = send_contact_details(args)

                # 4. Provide function call results to the model
                input_list.append({
                    "type": "function_call_output",
                    "call_id": item.call_id,
                    "output": json.dumps({
                        "func_response": func_response
                    })
                })

    # print("Final input:")
    # print(input_list)

    response = client.responses.create(
        model=GPT_MODEL,
        instructions=agent_prompt_main,
        tools=tools,
        input=input_list,
        conversation=conversation,
    )

    # 5. The model should be able to give a response!
    # print(response.model_dump_json(indent=2))
    return response.output_text, data_to_send
