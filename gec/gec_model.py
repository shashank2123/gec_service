import torch.nn as nn
import transformers


class config:
    MAX_LEN = 128
    BATCH_SIZE=16
    TOKENIZER_PATH = "resource\output"
    MODEL_PATH = "resource\output\pretrain-model.bin"
    TAG_ENCODER_PATH = "resource/output/tag_encoder.bin"
    BASE_MODEL_NAME = "bert-base-cased"
    TOKENIZER = transformers.AutoTokenizer.from_pretrained(
        TOKENIZER_PATH,
        do_lower_case=True,
        local_files_only=True
    )
    Bertconfig = transformers.BertConfig.from_pretrained(BASE_MODEL_NAME)

class GECModel(nn.Module):
    def __init__(self, num_tag):
        super(GECModel, self).__init__()
        self.num_tag = num_tag
        self.bert = transformers.AutoModel.from_config(config.Bertconfig)
        self.bert_drop = nn.Dropout(0.3)
        self.out_tag = nn.Linear(768, self.num_tag)
    
    def forward( self, ids, mask, token_type_ids, target_tag):

        output = self.bert(
            ids, 
            attention_mask=mask, 
            token_type_ids=token_type_ids
        )
        o1 = output["last_hidden_state"]

        bo_tag = self.bert_drop(o1)

        tag = self.out_tag(bo_tag)


        return tag

class TagEncoder():
  def __init__(self,PADDING_TOKEN="@@PADDING@@", UNK_TOKEN="@@UNKNOWN@@"):

    self.PADDING_TOKEN = PADDING_TOKEN
    self.UNK_TOKEN = UNK_TOKEN
    self.vocab = {}
    self.vocab[self.PADDING_TOKEN] = 0
    self.vocab[self.UNK_TOKEN] = 1
    self.reVocab = {}

  def fit(self, tags):
    
    for tag in tags:
      if tag not in self.vocab:
        self.vocab[tag]=len(self.vocab)

    for key, value in self.vocab.items():
      self.reVocab[value]=key

  def encode(self, tags):
    if tags in self.vocab:
      return self.vocab[tags]
    else:
        return self.vocab[self.UNK_TOKEN]

  def decode(self, tokens):
    if tokens in self.reVocab:
      return self.reVocab[tokens]
    else:
        raise "{} invalid Key".format(tokens)







