from transformers import AutoTokenizer, AutoModelForCausalLM
import transformers
import torch
import json

# Загрузка модели
model_name = "Vikhrmodels/Vikhr-Llama-3.2-1B-Instruct"
tokenizer = AutoTokenizer.from_pretrained(model_name, use_fast=False)
model = AutoModelForCausalLM.from_pretrained(model_name)


def get_response(prompt: str) -> str:
    input_ids = tokenizer.apply_chat_template([{"role": "user", "content": prompt}], truncation=True, add_generation_prompt=True, return_tensors="pt")
    outputs = model.generate(
            input_ids=input_ids,
            max_new_tokens=100,
    )

    #Декодирование полученного текста
    decoded_output = tokenizer.batch_decode(outputs, skip_special_tokens=False)[0]

    first_end_header_id = decoded_output.find('<|end_header_id|>')
    second_end_header_id = decoded_output.find('<|end_header_id|>', first_end_header_id + 1)
    third_end_header_id = decoded_output.find('<|end_header_id|>', second_end_header_id + 1)

    
    output_text = decoded_output[third_end_header_id + len('<|end_header_id|>'):].strip().replace('<|eot_id|>', '')
    return output_text


