import json
import glob

missing_cases = {
    'carteira.01': ['dante_01_452088859585966080l', 'dante_01_459167322549542912l', 'dante_01_443409354381750273l', 'dante_01_451423708167421952l', 'dante_01_461258410596368384l'],
    'recompra.01': ['dante_01_468731360044384256l', 'dante_01_458665044927332353l', 'dante_01_470972350767583232l', 'dante_01_470982638564806656l'],
    'compra.01': ['dante_01_446638058633699328l', 'dante_01_453631123914899457l'],
    'descoberta.01': ['dante_01_469952216032620544l', 'dante_01_469966875737473024l'],
    'proposta.01': ['dante_01_448061183451746304l', 'dante_01_456398217542766592l'],
    'comparação.01': ['dante_01_443438866146807809l'],
    'entrada.01': ['dante_01_452077337124028417l'],
    'olho.01': ['dante_01_460763680020647937l'],
    'posição.01': ['dante_01_446711741431676928l']
}

for roleset, sent_ids in missing_cases.items():
    json_path = f'D:\\OneDrive\\Documentos\\Ling\\IC\\Conversao em massa\\All Jsons\\{roleset.split(".")[0]}.json'
    # Fallback to search if the file is named slightly differently
    # Let's just use the exact name for now
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        for sent_id in sent_ids:
            count = 0
            for sense in data.get('senses', []):
                if sense.get('pt_roleset') == roleset:
                    for ex in sense.get('examples', []):
                        if sent_id in ex.get('sent_ID', '') or sent_id in ex.get('sent_id', ''):
                            count += 1
                            print(f'Match: {roleset} | {sent_id} | Args: {ex.get("realization")}')
            print(f'Total for {roleset} in {sent_id}: {count}')
            print('-'*40)
    except FileNotFoundError:
        print(f'File not found: {json_path}')
