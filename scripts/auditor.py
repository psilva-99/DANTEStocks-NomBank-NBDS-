import os
import json
import unicodedata
import re
import csv
import openpyxl
import difflib
import glob
from functools import lru_cache

# OTIMIZAÇÃO: Pré-compilar expressões regulares de uso intensivo
REGEX_PUNCTUATION = re.compile(r"[^\w\s]")
REGEX_CLEAN_ARG = re.compile(r'_\d+$')
REGEX_ARGM_LBL = re.compile(r'(argm-[a-z]+)')

CONTRACTIONS = {
    r'\bem o\b': 'no', r'\bem a\b': 'na', r'\bem os\b': 'nos', r'\bem as\b': 'nas',
    r'\bde o\b': 'do', r'\bde a\b': 'da', r'\bde os\b': 'dos', r'\bde as\b': 'das',
    r'\bde este\b': 'deste', r'\bde esta\b': 'desta', r'\bde estes\b': 'destes', r'\bde estas\b': 'destas',
    r'\bde esse\b': 'desse', r'\bde essa\b': 'dessa', r'\bde esses\b': 'desses', r'\bde essas\b': 'dessas',
    r'\bde aquele\b': 'daquele', r'\bde aquela\b': 'daquela', r'\bde aqueles\b': 'daqueles', r'\bde aquelas\b': 'daquelas',
    r'\bde aquilo\b': 'daquilo', r'\bde isso\b': 'disso', r'\bde isto\b': 'disto',
    r'\bem este\b': 'neste', r'\bem esta\b': 'nesta', r'\bem estes\b': 'nestes', r'\bem estas\b': 'nestas',
    r'\bem esse\b': 'nesse', r'\bem essa\b': 'nessa', r'\bem esses\b': 'nesses', r'\bem essas\b': 'nessas',
    r'\bem aquele\b': 'naquele', r'\bem aquela\b': 'naquela', r'\bem aqueles\b': 'naqueles', r'\bem aquelas\b': 'naquelas',
    r'\bem aquilo\b': 'naquilo', r'\bem isso\b': 'nisso', r'\bem isto\b': 'nisto',
    r'\bpor o\b': 'pelo', r'\bpor a\b': 'pela', r'\bpor os\b': 'pelos', r'\bpor as\b': 'pelas',
    r'\ba o\b': 'ao', r'\ba os\b': 'aos', r'\ba a\b': 'a', r'\ba as\b': 'as'
}

@lru_cache(maxsize=100000)
def normalize(text):
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.replace(",", ".")
    text = REGEX_PUNCTUATION.sub("", text)
    for pattern, replacement in CONTRACTIONS.items():
        text = re.sub(pattern, replacement, text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()
def load_expected_data(json_dir):
    expected_data = {}
    for fname in os.listdir(json_dir):
        if fname.endswith(".json"):
            with open(os.path.join(json_dir, fname), "r", encoding="utf-8") as f:
                try: data = json.load(f)
                except: continue
                if not isinstance(data, dict): continue
                for sense in data.get("senses", []):
                    roleset = sense.get("pt_roleset", "_")
                    for ex in sense.get("examples", []):
                        sent_id = ex.get("sent_ID") or ex.get("sent_id")
                        args = {k.lower(): v for k, v in ex.get("realization", {}).items() if v}
                        info = {"roleset": roleset, "args": args, "arquivo_origem": fname}
                        if sent_id:
                            sid = sent_id.strip()
                            if sid not in expected_data: expected_data[sid] = []
                            expected_data[sid].append(info)
                        tweet_text = ex.get("text")
                        if tweet_text:
                            nt = normalize(tweet_text)
                            if nt not in expected_data: expected_data[nt] = []
                            expected_data[nt].append(info)
    return expected_data

def load_argms_into_expected(excel_path, expected_data):
    tweet_map_keys_list = list(expected_data.keys())
    valid_keys_for_fuzzy = [k for k in tweet_map_keys_list if len(k) > 10]
    
    # Cache interno para evitar processamento repetitivo de difflib
    closest_tweet_cache = {}
    
    def get_closest_tweet_local(norm_tweet):
        if norm_tweet in closest_tweet_cache: return closest_tweet_cache[norm_tweet]
        if norm_tweet in expected_data:
            closest_tweet_cache[norm_tweet] = norm_tweet
            return norm_tweet
            
        for k in tweet_map_keys_list:
            if norm_tweet in k or k in norm_tweet:
                closest_tweet_cache[norm_tweet] = k
                return k
                
        matches = difflib.get_close_matches(norm_tweet, valid_keys_for_fuzzy, n=1, cutoff=0.7)
        if matches:
            closest_tweet_cache[norm_tweet] = matches[0]
            return matches[0]
            
        closest_tweet_cache[norm_tweet] = None
        return None

    import shutil, tempfile, os
    tmp_path = os.path.join(tempfile.gettempdir(), "temp_argm.xlsx")
    try: shutil.copy2(excel_path, tmp_path)
    except: pass
    import openpyxl
    wb = openpyxl.load_workbook(tmp_path, data_only=True)
    sheet = wb.worksheets[0]
    
    last_tweet = None
    
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i == 0 or row[0] == "Predicador": continue
        
        if row[1]: last_tweet = str(row[1]).strip()
        if not last_tweet: continue
        
        if len(row) < 3: continue
        argm_col = row[2]
        if not argm_col or str(argm_col).strip() == "-": continue
        argm_col = str(argm_col).strip()

        norm_tweet = normalize(last_tweet)
        best_match_key = get_closest_tweet_local(norm_tweet)
        
        if best_match_key:
            argm_col = argm_col.replace('; ARGM', '| ARGM').replace('; argm', '| argm')
            
            existing_norm_vals = {normalize(v) for v in expected_data[best_match_key][0]["args"].values()}
            
            for part in argm_col.split('|'):
                if ' - ' in part: parts = part.split(' - ', 1)
                elif ':' in part: parts = part.split(':', 1)
                elif '=' in part: parts = part.split('=', 1)
                else: parts = [part]
                if len(parts) < 2: continue
                lbl, txt = parts[0], parts[1]
                
                lbl_match = REGEX_ARGM_LBL.search(lbl.lower())
                clean_lbl = lbl_match.group(1) if lbl_match else lbl.strip().lower()
                txt = txt.split('(')[0].strip()
                
                if txt and clean_lbl:
                    txt_norm = normalize(txt)
                    if txt_norm not in existing_norm_vals:
                        existing_norm_vals.add(txt_norm)
                        base_lbl = clean_lbl
                        counter = 1
                        while base_lbl in expected_data[best_match_key][0]["args"]:
                            base_lbl = f"{clean_lbl}_{counter}"
                            counter += 1
                        expected_data[best_match_key][0]["args"][base_lbl] = txt

def validate_conllu(conllu_file, expected_data):
    with open(conllu_file, "r", encoding="utf-8") as f: content = f.read()
    blocks = content.split("\n\n")
    errors = []
    
    for block in blocks:
        if not block.strip(): continue
        lines = block.split("\n")
        sent_id, tweet_text = None, None
        found_rolesets, found_args = [], []
        
        for line in lines:
            if line.startswith("# sent_id ="): sent_id = line.replace("# sent_id =", "").strip()
            elif line.startswith("# text ="): tweet_text = line.replace("# text =", "").strip()
            elif not line.startswith("#") and line.strip():
                cols = line.split("\t")
                if len(cols) >= 12:
                    r_set, arg_str = cols[10], cols[11]
                    if r_set != "_":
                        for rs in r_set.split("|"): found_rolesets.append(rs)
                    if arg_str != "_":
                        for arg_item in arg_str.split("|"):
                            arg_name = arg_item.split(":")[0].lower()
                            found_args.append(arg_name)
        
        exp_infos = []
        if sent_id and sent_id in expected_data: 
            exp_infos = expected_data[sent_id]
        elif tweet_text:
            norm_tweet = normalize(tweet_text)
            if norm_tweet in expected_data: 
                exp_infos = expected_data[norm_tweet]
            
        for exp_info in exp_infos:
            exp_roleset, arquivo_origem = exp_info["roleset"], exp_info["arquivo_origem"]
            if exp_roleset in found_rolesets:
                found_rolesets.remove(exp_roleset)
            else:
                errors.append(f"[{arquivo_origem}] ERRO na sentença '{sent_id}': Roleset '{exp_roleset}' não anotado.")
            
            for arg_name, arg_text in exp_info["args"].items():
                clean_arg_name = REGEX_CLEAN_ARG.sub('', arg_name).lower()
                if clean_arg_name in found_args:
                    found_args.remove(clean_arg_name)
                else:
                    errors.append(f"[{arquivo_origem}] ERRO na sentença '{sent_id}': Argumento '{clean_arg_name.upper()}' ('{arg_text}') ausente.")
    return errors

if __name__ == "__main__":
    import argparse
    import sys
    import os
    import glob
    import re

    base_dir = os.path.dirname(os.path.abspath(__file__))
    root_dir = os.path.dirname(base_dir)
    if os.path.basename(base_dir) == "validacao argn e argm":
        root_dir = os.path.dirname(os.path.dirname(base_dir))
        
    parser = argparse.ArgumentParser(description="Validador de Anotações CoNLL-U Plus")
    parser.add_argument("--json-dir", default=os.path.join(root_dir, "data", "jsons"), help="Pasta com os JSONs (Padrão: ../data/jsons)")
    parser.add_argument("--excel-path", default=os.path.join(root_dir, "data", "argm.xlsx"), help="Caminho do Excel (Padrão: ../data/argm.xlsx)")
    parser.add_argument("--conllu-dir", default=os.path.join(root_dir, "output"), help="Pasta com os arquivos gerados (Padrão: ../output)")
    parser.add_argument("--log-dir", default=os.path.join(root_dir, "logs"), help="Pasta de logs (Padrão: ../logs)")
    
    args = parser.parse_args()
    
    if not os.path.isdir(args.json_dir):
        print(f"Erro: A pasta '{args.json_dir}' não foi encontrada.")
        sys.exit(1)
    if not os.path.isfile(args.excel_path):
        print(f"Erro: O arquivo '{args.excel_path}' não foi encontrado.")
        sys.exit(1)
    if not os.path.isdir(args.conllu_dir):
        print(f"Erro: A pasta '{args.conllu_dir}' não foi encontrada.")
        sys.exit(1)

    os.makedirs(args.log_dir, exist_ok=True)
    
    conllu_files = glob.glob(os.path.join(args.conllu_dir, "*.conllup"))
    if not conllu_files:
        print(f"Aviso: Nenhum arquivo .conllup encontrado em '{args.conllu_dir}'.")
        sys.exit(0)

    log_content = []
    def log_print(msg):
        print(msg)
        log_content.append(str(msg))

    log_print("Carregando o Gabarito Unificado...")
    expected_data = load_expected_data(args.json_dir)
    load_argms_into_expected(args.excel_path, expected_data)

    for conllu_file in conllu_files:
        log_print(f"\n--- Analisando arquivo: {os.path.basename(conllu_file)} ---")
        erros = validate_conllu(conllu_file, expected_data)
        if not erros: log_print("[OK] VALIDAÇÃO CONCLUÍDA SEM ERROS!")
        else:
            for e in erros: log_print(e)
            
    version = 10
    existing_logs = glob.glob(os.path.join(args.log_dir, f"log V{version} *.txt"))
    max_y = 0
    for log_path in existing_logs:
        fname = os.path.basename(log_path)
        match = re.search(rf"log V{version}\s+(\d+)\.txt", fname)
        if match:
            y_val = int(match.group(1))
            if y_val > max_y: max_y = y_val
            
    next_y = max_y + 1
    log_filename = os.path.join(args.log_dir, f"log V{version} {next_y}.txt")
    
    with open(log_filename, "w", encoding="utf-8") as f:
        f.write("\n".join(log_content))
    print(f"\n>>> Arquivo de log salvo com sucesso em: {log_filename}")
