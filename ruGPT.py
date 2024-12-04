import yaml
from typing import Optional
from transformers import GPT2LMHeadModel, GPT2Tokenizer
from dotenv import load_dotenv
import os

def load_config(config_path:str ='config.yaml'):
    with open(config_path, 'r') as file:
        config = yaml.safe_load(file)
    return config


# Загрузка модели
load_dotenv()
config = load_config()
path = os.getenv("ruGPT_PATH")
try:
    tokenizer = GPT2Tokenizer.from_pretrained(path)
    model = GPT2LMHeadModel.from_pretrained(path)
except Exception as e:
    print(f"Ошибка при загрузке модели или токенизатора: {e}")


'''
# early_stopping=True — генерация подсчёта вероятностей завершается, когда достигнут конец предложения.
top_k – определяется n кол-во слов, которые обладают наибольшей вероятностью из условного распределения вероятностей всех слов
top_p – определяется n слов, чья вероятностная масса вместе равна n%
temperature – используя данный коэффициент происходит увеличение вероятности использования слов с высокими значениями вероятности 
            и уменьшение вероятности использования слов с низкой вероятностью в распределении
num_beams – кол-во путей с наибольшими неочевидными итоговыми вероятностными сочетаниями
no_repeat_ngram_size # – штраф за повторы в сочетаниях слов. Убирает повторы длиной в n слов
'''



def generate_annotation(topic: str,
                        top_k: Optional[int] = None,
                        top_p: Optional[float] = None,
                        temperature: Optional[float] = None) -> str:

    # Кодирование входного текста
    input_ids = tokenizer.encode(topic, return_tensors="pt")
    # Создание attention_mask
    attention_mask = input_ids != tokenizer.pad_token_id

    # Получение параметров из конфигурации, если они не переданы явно
    top_k = top_k or config['model_annotation']['top_k']
    top_p = top_p or config['model_annotation']['top_p']
    temperature = temperature or config['model_annotation']['temperature']

    # Генерация текста
    out = model.generate(input_ids,
                        max_length=config['model_annotation']['max_length'],
                        min_length=config['model_annotation']['min_length'],
                        num_return_sequences=config['model_annotation']['num_return_sequences'],
                        temperature=temperature,
                        top_k=top_k,
                        top_p=top_p,
                        do_sample=True,
                        attention_mask=attention_mask,
                        no_repeat_ngram_size=config['model_annotation']['no_repeat_ngram_size'],
                        num_beams=config['model_annotation']['num_beams'],
                        early_stopping=config['model_annotation']['early_stopping'],)

    # Декодирование выходного текста
    generated_text:str = tokenizer.decode(out[0], skip_special_tokens=True)
    return generated_text