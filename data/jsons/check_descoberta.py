import json

with open(r'D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons\descoberta.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for sense in data.get('senses', []):
    for ex in sense.get('examples', []):
        if '469966875737473024' in ex.get('sent_ID', '') or '469966875737473024' in ex.get('sent_id', ''):
            print(f'Roleset: {sense.get("pt_roleset")} | Text: {ex.get("text")} | Args: {ex.get("realization")}')
