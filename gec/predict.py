from gec.gec_model import config, GECModel
import torch
import joblib
from nltk.tokenize import TweetTokenizer

from gec.helpers import PAD, UNK, get_target_sent_by_edits, START_TOKEN

class Prediction:
    def __init__(self):

        self.decoder = joblib.load(config.TAG_ENCODER_PATH)["enc_tag"]
        self.num_tag = len(self.decoder.vocab)
        self.device = torch.device("cuda")
        self.model = GECModel(num_tag=self.num_tag)
        self.model.load_state_dict(torch.load(config.MODEL_PATH))
        self.model.to(self.device)

    def get_batch(self, sentence):

        ids = []
        word_ids = []

        for i, s in enumerate(sentence):
            inputs = config.TOKENIZER.encode(s,add_special_tokens=False)
        
            input_len = len(inputs)
            ids.extend(inputs)
            word_ids.extend([i]*input_len)

        ids_list = []
        mask_list = []
        token_type_ids_list = []
        last_limit = 0

        for i in range(0, len(ids), config.MAX_LEN-2):
            idx = ids[i:i+config.MAX_LEN-2]
            idx = [101] + idx + [102]   
            mask = [1] * len(idx)
            token_type_ids = [0] * len(idx)

            last_limit = len(idx)

            padding_len = config.MAX_LEN - len(idx)

            idx = idx + ([0] * padding_len)
            mask = mask + ([0] * padding_len)
            token_type_ids = token_type_ids + ([0] * padding_len)

            ids_list.append(idx)
            mask_list.append(mask)
            token_type_ids_list.append(token_type_ids)

        batch_inputs = []

        for i in range(0, len(ids_list), config.BATCH_SIZE):

            batch_ids = ids_list[i:i+config.BATCH_SIZE]
            batch_mask = mask_list[i:i+config.BATCH_SIZE]
            batch_token_type_ids = token_type_ids_list[i:i+config.BATCH_SIZE]
            batch_target = [[0]*config.MAX_LEN for _ in range(config.BATCH_SIZE)]

            batch = {
                "ids": torch.tensor(batch_ids, dtype=torch.long),
                "mask": torch.tensor(batch_mask, dtype=torch.long),
                "token_type_ids": torch.tensor(batch_token_type_ids, dtype=torch.long),
                "target_tag": torch.tensor(batch_target, dtype=torch.long),
            }

            batch_inputs.append(batch)
        
        return batch_inputs, word_ids, last_limit


    def tag_extractor(self, batch_tag, sentence, word_ids):

        tags = []

        for batch in batch_tag:
            for tag_list in batch:
                tags.extend(tag_list[1:-1])

        output_tags = [""]*len(sentence)
        i=0
        for idx in word_ids:
            if output_tags[idx]=="" and tags[i]!=0:
                output_tags[idx]=self.decoder.decode(tags[i])
            i+=1
        
        return output_tags


    def post_processing(self, tokens, suggestion_tags):
        
        return get_target_sent_by_edits(tokens, suggestion_tags)

    def predict(self, text):

        sentence = TweetTokenizer().tokenize(text)

        batch_input, word_ids, last_limit = self.get_batch(sentence=sentence)

        batch_output_tags = []

        for batch in batch_input:
            with torch.no_grad():
                for k, v in batch.items():
                    batch[k] = v.to(self.device)
                tag = self.model(**batch)

            pred = list(tag.argmax(2).cpu().numpy())
            batch_output_tags.append(pred)
        
        batch_output_tags[-1][-1]=batch_output_tags[-1][-1][:last_limit]

        output_tags = self.tag_extractor(batch_output_tags, sentence, word_ids)
        corrections = self.post_processing(sentence, output_tags)
        return corrections






