import os
import string
from unittest import result


VOCAB_DIR =  "resource\data"
PAD = "@@PADDING@@"
UNK = "@@UNKNOWN@@"
START_TOKEN = "$START"
SEQ_DELIMETERS = {"tokens": " ",
                  "labels": "SEPL|||SEPR",
                  "operations": "SEPL__SEPR"}
REPLACEMENTS = {
    "''": '"',
    '--': '—',
    '`': "'",
    "'ve": "' ve",
}


def get_verb_form_dicts():
    path_to_dict = os.path.join(VOCAB_DIR, "verb-form-vocab.txt")
    encode, decode = {}, {}
    with open(path_to_dict, encoding="utf-8") as f:
        for line in f:
            words, tags = line.split(":")
            word1, word2 = words.split("_")
            tag1, tag2 = tags.split("_")
            decode_key = f"{word1}_{tag1}_{tag2.strip()}"
            if decode_key not in decode:
                encode[words] = tags
                decode[decode_key] = word2
    return encode, decode


ENCODE_VERB_DICT, DECODE_VERB_DICT = get_verb_form_dicts()


def get_target_sent_by_edits(source_tokens, suggetion_token):
    correction_tokens = []

    for token,sugg in zip(source_tokens, suggetion_token):
    
        if sugg.startswith("$APPEND_"):
            word = sugg.replace("$APPEND_", "")
            correction = append_word(token, word)
        elif sugg.startswith("$TRANSFORM_"):
            correction = apply_reverse_transformation(token, sugg)
        elif sugg.startswith("$REPLACE_"):
            word = sugg.replace("$REPLACE_", "")
            correction =  {
                "orig_token":token, 
                "sugg_token":word,
                "tag_class":"REPLACE",
                "description": f"The word {token} is replacing with {word}"
                }
        elif sugg.startswith("$MERGE_"):
            action = sugg.replace("$MERGE_", "")
            word = token + " "+ sugg
            correction = {
                "orig_token":token, 
                "sugg_token":word,
                "tag_class":"MERGE",
                "description": f"The word {token} is Merging with {action}"
                }
        elif sugg=="$DELETE":
            correction =   {
                "orig_token":token, 
                "sugg_token":"",
                "tag_class":"DELETE",
                "description": f"Deleting word {token}"
                }
        else:
            correction =   {
                "orig_token":token, 
                "sugg_token":token,
                "tag_class":"KEEP",
                "description": f"No Changes"
                }

        correction_tokens.append(correction)
    return correction_tokens

def append_word(token, word):
    
    if word not in string.punctuation:
        target_token = token + " " + word
    else:
        target_token = token+word

    result = {
        "orig_token":token, 
        "sugg_token":target_token,
        "tag_class":"APPEND",
        "description": f"The word {token} is appending with {word}"
        }

    return result


def convert_using_case(token, smart_action):
    if not smart_action.startswith("$TRANSFORM_CASE_"):
        return token
    if smart_action.endswith("LOWER"):
        return token.lower()
    elif smart_action.endswith("UPPER"):
        return token.upper()
    elif smart_action.endswith("CAPITAL"):
        return token.capitalize()
    elif smart_action.endswith("CAPITAL_1"):
        return token[0] + token[1:].capitalize()
    elif smart_action.endswith("UPPER_-1"):
        return token[:-1].upper() + token[-1]
    else:
        return token


def convert_using_verb(token, smart_action):
    key_word = "$TRANSFORM_VERB_"
    if not smart_action.startswith(key_word):
        raise Exception(f"Unknown action type {smart_action}")
    encoding_part = f"{token}_{smart_action[len(key_word):]}"
    decoded_target_word = decode_verb_form(encoding_part)
    return decoded_target_word


def convert_using_split(token, smart_action):
    key_word = "$TRANSFORM_SPLIT"
    if not smart_action.startswith(key_word):
        raise Exception(f"Unknown action type {smart_action}")
    target_words = token.split("-")
    return " ".join(target_words)


def convert_using_plural(token, smart_action):
    if smart_action.endswith("PLURAL"):
        return token + "s"
    elif smart_action.endswith("SINGULAR"):
        return token[:-1]
    else:
        raise Exception(f"Unknown action type {smart_action}")


def apply_reverse_transformation(source_token, transform):
    if transform.startswith("$TRANSFORM"):
        # deal with case
        if transform.startswith("$TRANSFORM_CASE"):
            word = convert_using_case(source_token, transform)
            result = {
                "orig_token":source_token, 
                "sugg_token": word,
                "tag_class":"TRANSFORM",
                "description": f"Changing Case of word from {source_token} to {word}"
                }
            return result
        # deal with verb
        if transform.startswith("$TRANSFORM_VERB"):
            word = convert_using_verb(source_token, transform)
            result = {
                "orig_token":source_token, 
                "sugg_token": word,
                "tag_class":"TRANSFORM",
                "description": f"Changing Verb of word from {source_token} to {word}"
                }
            return result
        # deal with split
        if transform.startswith("$TRANSFORM_SPLIT"):
            word = convert_using_split(source_token, transform)
            result = {
                "orig_token":source_token, 
                "sugg_token": word,
                "tag_class":"TRANSFORM",
                "description": f"Spliting from {source_token} to {word}"
                }
            return result
        # deal with single/plural
        if transform.startswith("$TRANSFORM_AGREEMENT"):
            word = convert_using_plural(source_token, transform)
            result = {
                "orig_token":source_token, 
                "sugg_token": word,
                "tag_class":"TRANSFORM",
                "description": f"Changing single/prural of word from {source_token} to {word}"
                }

            return result
        # raise exception if not find correct type
        raise Exception(f"Unknown action type {transform}")
    else:
        return source_token


def read_parallel_lines(fn1, fn2):
    lines1 = read_lines(fn1, skip_strip=True)
    lines2 = read_lines(fn2, skip_strip=True)
    assert len(lines1) == len(lines2)
    out_lines1, out_lines2 = [], []
    for line1, line2 in zip(lines1, lines2):
        if not line1.strip() or not line2.strip():
            continue
        else:
            out_lines1.append(line1)
            out_lines2.append(line2)
    return out_lines1, out_lines2


def read_lines(fn, skip_strip=False):
    if not os.path.exists(fn):
        return []
    with open(fn, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return [s.strip() for s in lines if s.strip() or skip_strip]


def write_lines(fn, lines, mode='w'):
    if mode == 'w' and os.path.exists(fn):
        os.remove(fn)
    with open(fn, encoding='utf-8', mode=mode) as f:
        f.writelines(['%s\n' % s for s in lines])


def decode_verb_form(original):
    return DECODE_VERB_DICT.get(original)


def encode_verb_form(original_word, corrected_word):
    decoding_request = original_word + "_" + corrected_word
    decoding_response = ENCODE_VERB_DICT.get(decoding_request, "").strip()
    if original_word and decoding_response:
        answer = decoding_response
    else:
        answer = None
    return answer


def get_weights_name(transformer_name, lowercase):
    if transformer_name == 'bert' and lowercase:
        return 'bert-base-uncased'
    if transformer_name == 'bert' and not lowercase:
        return 'bert-base-cased'
    if transformer_name == 'bert-large' and not lowercase:
        return 'bert-large-cased'
    if transformer_name == 'distilbert':
        if not lowercase:
            print('Warning! This model was trained only on uncased sentences.')
        return 'distilbert-base-uncased'
    if transformer_name == 'albert':
        if not lowercase:
            print('Warning! This model was trained only on uncased sentences.')
        return 'albert-base-v1'
    if lowercase:
        print('Warning! This model was trained only on cased sentences.')
    if transformer_name == 'roberta':
        return 'roberta-base'
    if transformer_name == 'roberta-large':
        return 'roberta-large'
    if transformer_name == 'gpt2':
        return 'gpt2'
    if transformer_name == 'transformerxl':
        return 'transfo-xl-wt103'
    if transformer_name == 'xlnet':
        return 'xlnet-base-cased'
    if transformer_name == 'xlnet-large':
        return 'xlnet-large-cased'


def remove_double_tokens(sent):
    tokens = sent.split(' ')
    deleted_idx = []
    for i in range(len(tokens) -1):
        if tokens[i] == tokens[i + 1]:
            deleted_idx.append(i + 1)
    if deleted_idx:
        tokens = [tokens[i] for i in range(len(tokens)) if i not in deleted_idx]
    return ' '.join(tokens)


def normalize(sent):
    sent = remove_double_tokens(sent)
    for fr, to in REPLACEMENTS.items():
        sent = sent.replace(fr, to)
    return sent.lower()
