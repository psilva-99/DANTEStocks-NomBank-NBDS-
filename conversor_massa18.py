import os
import json
import unicodedata
import re
import difflib
import csv
import openpyxl

REGEX_PUNCT = re.compile(r"[^\w\s]")
REGEX_ARGM = re.compile(r'(argm-[a-z]+)')

def normalize(text):
    text = text.lower()
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    text = text.replace(",", ".")
    text = REGEX_PUNCT.sub("", text)
    return text.strip()

def get_closest_tweet(norm_tweet, tweet_map, tweet_map_keys, valid_keys):
    if norm_tweet in tweet_map: return norm_tweet 
    
    if len(norm_tweet) >= 15:
        for k in tweet_map_keys:
            if len(k) >= 15 and (norm_tweet in k or k in norm_tweet): 
                return k
        
    matches = difflib.get_close_matches(norm_tweet, valid_keys, n=1, cutoff=0.60) 
    if matches: return matches[0]
    return None

def load_rolesets(json_dir):
    rolesets, tweet_map = {}, {}
    for fname in os.listdir(json_dir):
        if fname.endswith(".json"):
            with open(os.path.join(json_dir, fname), "r", encoding="utf-8") as f:
                try: data = json.load(f)
                except: continue
                if isinstance(data, dict) and "lemma" in data:
                    lemma = data.get("lemma")
                    senses = data.get("senses", [])
                    if lemma and senses:
                        rolesets[lemma.lower()] = []
                        for sense in senses:
                            roleset = sense.get("pt_roleset", "_")
                            for ex in sense.get("examples", []):
                                args = {k: v for k, v in ex.get("realization", {}).items() if v}
                                tweet_text, sent_id = ex.get("text"), (ex.get("sent_ID") or ex.get("sent_id"))
                                info = {"lemma": lemma, "roleset": roleset, "args": args.copy()}
                                
                                if sent_id:
                                    sid = sent_id.strip()
                                    if sid not in tweet_map: tweet_map[sid] = []
                                    tweet_map[sid].append(info)
                                        
                                if tweet_text:
                                    nt = normalize(tweet_text)
                                    if nt not in tweet_map: tweet_map[nt] = []
                                    tweet_map[nt].append(info)
                                        
                                rolesets[lemma.lower()].append(info)
    return rolesets, tweet_map

def load_argms(excel_path, tweet_map):
    tweet_map_keys = list(tweet_map.keys())
    valid_keys = [k for k in tweet_map_keys if len(k) >= 15] 
    
    import shutil, tempfile, os
    tmp_path = os.path.join(tempfile.gettempdir(), "temp_argm.xlsx")
    try: shutil.copy2(excel_path, tmp_path)
    except: pass
    import openpyxl
    wb = openpyxl.load_workbook(tmp_path, data_only=True)
    sheet = wb.worksheets[0]
    
    last_predicador = None
    last_tweet = None
    
    for i, row in enumerate(sheet.iter_rows(values_only=True)):
        if i == 0 or row[0] == "Predicador": continue # Skip header
        
        # State machine herança (mesclagem de células)
        if row[0]: last_predicador = str(row[0]).strip().lower()
        if row[1]: last_tweet = str(row[1]).strip()
        
        if not last_predicador or not last_tweet: continue
        
        if len(row) < 3: continue
        argm_col = row[2]
        if not argm_col or str(argm_col).strip() == "-": continue
        argm_col = str(argm_col).strip()
        
        norm_tweet = normalize(last_tweet)
        best_match_key = get_closest_tweet(norm_tweet, tweet_map, tweet_map_keys, valid_keys)
        
        if best_match_key:
            target_infos = tweet_map[best_match_key]
            info_match = None
            
            # Match pelo lema do predicador na planilha Excel (ex: 'aditivo' ao invés de 'aditivo.01')
            for info in target_infos:
                if info["lemma"].lower() == last_predicador or info["roleset"].lower().startswith(last_predicador) or info["lemma"].lower() in last_predicador or last_predicador in info["lemma"].lower():
                    info_match = info
                    break
                    
            if not info_match and last_predicador:
                roleset_guess = f"{last_predicador}.01"
                info_match = {"lemma": last_predicador, "roleset": roleset_guess, "args": {}}
                target_infos.append(info_match)
                
            if not info_match:
                info_match = target_infos[0]
                
            argm_col = argm_col.replace('; ARGM', '| ARGM').replace('; argm', '| argm')
            for part in argm_col.split('|'):
                # Regex split to handle both 'ARGM-TMP: ontem', 'ARGM-TMP - ontem' and 'ARGM-TMP=ontem'
                if ' - ' in part: parts = part.split(' - ', 1)
                elif ':' in part: parts = part.split(':', 1)
                elif '=' in part: parts = part.split('=', 1)
                else: parts = [part]
                if len(parts) < 2: continue
                lbl, txt = parts[0], parts[1]
                
                lbl_match = REGEX_ARGM.search(lbl.lower())
                clean_lbl = lbl_match.group(1) if lbl_match else lbl.strip().lower()
                txt = txt.split('(')[0].strip()
                
                if txt and clean_lbl:
                    txt_norm = normalize(txt)
                    if not any((normalize(v) == txt_norm and k.lower().startswith(clean_lbl)) for k, v in info_match["args"].items()):
                        base_lbl = clean_lbl
                        counter = 1
                        while base_lbl in info_match["args"]:
                            base_lbl = f"{clean_lbl}_{counter}"
                            counter += 1
                        info_match["args"][base_lbl] = txt

def find_span_head(sentence_tokens, arg_text, pred_id=None):
    arg_norm_words = [nw for nw in (normalize(w) for w in arg_text.split()) if nw]
    if not arg_norm_words: return None
    
    filtered_sent_norms = []
    filtered_indices = []
    for i, tok in enumerate(sentence_tokens):
        if tok[5]:
            filtered_sent_norms.append(tok[5])
            filtered_indices.append(i)
            
    span_indices = set()
    arg_len = len(arg_norm_words)
    
    if arg_len > 0:
        for i in range(len(filtered_sent_norms) - arg_len + 1):
            if filtered_sent_norms[i:i+arg_len] == arg_norm_words:
                start_orig_idx = filtered_indices[i]
                end_orig_idx = filtered_indices[i+arg_len-1]
                for j in range(start_orig_idx, end_orig_idx + 1):
                    span_indices.add(j)
                break
                
    if not span_indices:
        for aw in sorted(arg_norm_words, key=len, reverse=True):
            if len(aw) < 2: continue
            for i, tok in enumerate(sentence_tokens):
                sn = tok[5]
                if sn and (sn == aw or (len(aw) > 3 and difflib.get_close_matches(aw, [sn], n=1, cutoff=0.7))):
                    span_indices.add(i)
                    break
            if span_indices: break

    if not span_indices:
        for aw in sorted(arg_norm_words, key=len, reverse=True):
            if len(aw) < 2: continue
            for i, tok in enumerate(sentence_tokens):
                f_norm, l_norm = tok[5], tok[6]
                if (f_norm and aw.startswith(f_norm) and len(f_norm) >= 2) or \
                   (l_norm and aw.startswith(l_norm) and len(l_norm) >= 2) or \
                   (f_norm and f_norm in aw and len(f_norm) >= 3):
                    span_indices.add(i)
                    break
            if span_indices: break

    if not span_indices and any(c.isdigit() for c in arg_text):
        for i, tok in enumerate(sentence_tokens):
            if tok[3] == "NUM":
                span_indices.add(i)
                break

    if not span_indices: return None
        
    span_tids = {sentence_tokens[i][0] for i in span_indices}
    candidates = []
    
    ordered_span_indices = sorted(list(span_indices))
    
    for i in ordered_span_indices:
        tid, form, lemma, upos, head, nf, nl = sentence_tokens[i]
        if head not in span_tids:
            candidates.append(tid)
            
    chosen_head = candidates[0] if candidates else sentence_tokens[ordered_span_indices[0]][0]

    if pred_id and pred_id in span_tids and len(span_tids) > 1:
        dep_counts = {}
        for i in span_indices:
            token_head = sentence_tokens[i][4] 
            if token_head in span_tids:
                dep_counts[token_head] = dep_counts.get(token_head, 0) + 1
                
        best_cand = None
        max_deps = -1
        
        for tid in span_tids:
            if tid == pred_id: continue 
            count = dep_counts.get(tid, 0)
            if count > max_deps:
                max_deps = count
                best_cand = tid
                
        if best_cand:
            chosen_head = best_cand
        else:
            for i in ordered_span_indices:
                cand_tid = sentence_tokens[i][0]
                if cand_tid != pred_id:
                    chosen_head = cand_tid
                    break

    return chosen_head

def process_conllu_block(block_lines, rolesets, tweet_map):
    output = []
    clean_block = [line for line in block_lines if not line.startswith("# global.columns")]
    output.append("# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC NBDS:ROLESET NBDS:ARG")

    tweet_text, sent_id = None, None
    for line in clean_block:
        if line.startswith("# text ="): tweet_text = line.replace("# text =", "").strip()
        elif line.startswith("# sent_id ="): sent_id = line.replace("# sent_id =", "").strip()

    tweet_infos = [] 
    if sent_id and sent_id in tweet_map: tweet_infos = tweet_map[sent_id]
    elif tweet_text and normalize(tweet_text) in tweet_map: tweet_infos = tweet_map[normalize(tweet_text)]

    sentence_tokens = [] 
    for line in clean_block:
        if not line.strip() or line.startswith("#"): continue
        cols = line.split("\t")
        if len(cols) < 10: continue
        tid, form, lemma, upos, head = cols[0], cols[1], cols[2], cols[3], cols[6]
        if "-" in tid or "." in tid: continue
        sentence_tokens.append((tid, form, lemma, upos, head, normalize(form), normalize(lemma)))



    roleset_mappings = {}
    arg_mappings = {}
    used_pred_ids = set()
    
    for info in tweet_infos:
        pred_id = None
        if "_fallback_tid" in info:
            pred_id = info["_fallback_tid"]
        else:
            target_lemma = normalize(info["lemma"])
            
            for tok in sentence_tokens:
                if tok[0] not in used_pred_ids and (tok[6] == target_lemma or tok[5] == target_lemma):
                    pred_id = tok[0]; break
                    
            if not pred_id:
                available = [t[6] for t in sentence_tokens if t[0] not in used_pred_ids] + [t[5] for t in sentence_tokens if t[0] not in used_pred_ids]
                matches = difflib.get_close_matches(target_lemma, available, n=1, cutoff=0.7)
                if matches:
                    best = matches[0]
                    for tok in sentence_tokens:
                        if tok[0] not in used_pred_ids and (tok[6] == best or tok[5] == best):
                            pred_id = tok[0]; break
                            
            if not pred_id:
                for tok in sentence_tokens:
                    if tok[0] in used_pred_ids: continue
                    fn, ln = tok[5], tok[6]
                    if (len(fn) >= 4 and fn in target_lemma) or (len(ln) >= 4 and ln in target_lemma):
                        pred_id = tok[0]; break
                        
            if not pred_id:
                for tok in sentence_tokens:
                    if tok[0] in used_pred_ids: continue
                    fn, ln = tok[5], tok[6]
                    if (fn and target_lemma.startswith(fn) and len(fn) >= 2) or \
                       (ln and target_lemma.startswith(ln) and len(ln) >= 2):
                        pred_id = tok[0]; break
                        
        if pred_id:
            used_pred_ids.add(pred_id)
            if pred_id not in roleset_mappings:
                roleset_mappings[pred_id] = info["roleset"]
            else:
                if info["roleset"] not in roleset_mappings[pred_id]:
                    roleset_mappings[pred_id] += "|" + info["roleset"]

            for arg_id, arg_text in info["args"].items():
                if arg_text:
                    token_id = find_span_head(sentence_tokens, arg_text, pred_id)
                    if not token_id: token_id = pred_id
                        
                    if token_id:
                        clean_arg_id = re.sub(r'_\d+$', '', arg_id.lower())
                        label = f"{clean_arg_id}:{pred_id}"
                        
                        if token_id not in arg_mappings: arg_mappings[token_id] = []
                        if label not in arg_mappings[token_id]: arg_mappings[token_id].append(label)

    for line in clean_block:
        if not line.strip(): continue
        if line.startswith("#"):
            output.append(line)
            continue

        cols = line.split("\t")
        if len(cols) < 10: cols.extend(["_"] * (10 - len(cols)))
        
        tid = cols[0]
        roleset, argn = "_", "_"

        if "-" not in tid and "." not in tid:
            if tid in roleset_mappings: roleset = roleset_mappings[tid]
            if tid in arg_mappings: argn = "|".join(arg_mappings[tid])

        cols = cols[:10] + [roleset, argn]
        if len(cols) < 12: cols.extend(["_"] * (12 - len(cols)))
        output.append("\t".join(cols))

    output.append("")
    return output

if __name__ == "__main__":
    json_dir = r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\All Jsons"
    excel_path = r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\argms isa\Geral - ArgM.xlsx"
    output_dir = r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\saída"
    
    input_files = [
        r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\V3_UD\DANTEStocks-dev.conllu",
        r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\V3_UD\DANTEStocks-test.conllu",
        r"D:\OneDrive\Documentos\Ling\IC\Conversao em massa\V3_UD\DANTEStocks-train.conllu"
    ]

    os.makedirs(output_dir, exist_ok=True)

    print("Carregando e indexando JSONs em memória...")
    rolesets, tweet_map = load_rolesets(json_dir)
    print("Processando ARGMs e fundindo com o gabarito principal...")
    load_argms(excel_path, tweet_map)

    for input_txt in input_files:
        filename = os.path.basename(input_txt)
        nome_base, ext = os.path.splitext(filename)
        output_txt = os.path.join(output_dir, f"{nome_base} (conllu plus){ext}")
        
        print(f"\nConvertendo '{filename}'...")
        with open(input_txt, "r", encoding="utf-8") as f: lines = f.readlines()

        blocks, current_block, unique_sent_ids = [], [], set()
        for line in lines:
            if line.strip() == "" and current_block:
                blocks.append(current_block)
                current_block = []
            else:
                current_block.append(line.rstrip("\n"))
                if line.startswith("# sent_id ="): unique_sent_ids.add(line.replace("# sent_id =", "").strip())
        if current_block: blocks.append(current_block)

        output_lines = []
        for block in blocks: output_lines.extend(process_conllu_block(block, rolesets, tweet_map))

        with open(output_txt, "w", encoding="utf-8") as f: f.write("\n".join(output_lines))
        print(f"[OK] Salvo como '{os.path.basename(output_txt)}' (Total de tweets: {len(unique_sent_ids)})")
