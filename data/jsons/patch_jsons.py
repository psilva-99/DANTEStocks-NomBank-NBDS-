import json

# Fix proposta.json
with open(r'D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons\proposta.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['senses']:
    if s['pt_roleset'] == 'proposta.01':
        # Remove the second occurrence for 448061183451746304
        seen_1 = False
        new_ex = []
        for ex in s['examples']:
            if '448061183451746304' in ex['sent_ID']:
                if not seen_1:
                    seen_1 = True
                    new_ex.append(ex)
            elif '456398217542766592' in ex['sent_ID']:
                if 'seen_2' not in locals():
                    seen_2 = True
                    new_ex.append(ex)
            else:
                new_ex.append(ex)
        s['examples'] = new_ex

with open(r'D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons\proposta.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)


# Fix compra.json
with open(r'D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons\compra.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for s in data['senses']:
    if s['pt_roleset'] == 'compra.01':
        new_ex = []
        for ex in s['examples']:
            if '446638058633699328' in ex['sent_ID']:
                # The word "compra" doesn't even exist in this sentence. Remove it completely.
                pass
            else:
                new_ex.append(ex)
        s['examples'] = new_ex

with open(r'D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons\compra.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=4)
