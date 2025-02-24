import json
import re
from transformers import T5Tokenizer, T5ForConditionalGeneration, M2M100ForConditionalGeneration, M2M100Tokenizer

# Load T5 model for summarization
model_name = "t5-base"
tokenizer_summ = T5Tokenizer.from_pretrained(model_name)
model_summ = T5ForConditionalGeneration.from_pretrained(model_name)

# Load M2M100 model for translation
model_name_trans = "facebook/m2m100_418M"
tokenizer_trans = M2M100Tokenizer.from_pretrained(model_name_trans)
model_trans = M2M100ForConditionalGeneration.from_pretrained(model_name_trans)

def clean_text(text):
    """Clean text by removing newlines, extra spaces, and unwanted characters."""
    text = re.sub(r"\n+", " ", text)  # Remove newlines
    text = re.sub(r"\s+", " ", text)  # Remove multiple spaces
    text = re.sub(r"[^a-zA-Z0-9,.\-:;()'\"\s]", "", text)  # Keep common punctuation

    return text.strip()

def summarize_text(text):
    """Summarize text using the T5 model."""
    input_text = f"summarize: {text}"
    inputs = tokenizer_summ.encode(input_text, return_tensors="pt", max_length=512, truncation=True)
    summary_ids = model_summ.generate(inputs, max_length=150, num_beams=4, length_penalty=1.0, no_repeat_ngram_size=2, early_stopping=True)
    return tokenizer_summ.decode(summary_ids[0], skip_special_tokens=True)

def translate_text(text):
    """Translate English text to Hindi using M2M100."""
    tokenizer_trans.src_lang = "en"
    encoded_text = tokenizer_trans(text, return_tensors="pt")
    output_tokens = model_trans.generate(**encoded_text, forced_bos_token_id=tokenizer_trans.get_lang_id("hi"))
    translated_text = tokenizer_trans.decode(output_tokens[0], skip_special_tokens=True)
    return translated_text.replace(".", "।")  # Replace full stop with Hindi "Poorn Viram"

# POST PROCESSING THE OUTPUT:
def fix_punctuation(text):
    # Capitalize the first letter of each sentence
    text = re.sub(r"([.!?]\s+)([a-z])", lambda p: p.group(1) + p.group(2).upper(), text)
    # Capitalize the very first letter if needed
    text = text[0].upper() + text[1:] if text else ""
    return text

def process_json(input_file, output_file):
    """Load, process, and save the JSON file."""
    try:
        with open(input_file, "r", encoding="utf-8") as f:
            articles = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: '{input_file}' file not found.")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON format in '{input_file}'.")
        return

    for article in articles:
        content = article.get("content", "")
        if content:
            cleaned_text = clean_text(content)
            summary = summarize_text(cleaned_text)
            translated_text = translate_text(summary)
            article["summary"] = fix_punctuation(summary)
            article["translated_text"] = translated_text
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Processed JSON saved to {output_file}")

if __name__ == "__main__":  # Fixed the entry point
    input_json = "toi_articles.json"  # JSON file generated by scraper
    output_json = "processed_articles.json"  # Output JSON file with summaries
    process_json(input_json, output_json)
