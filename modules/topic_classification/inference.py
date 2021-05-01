import pandas as pd
import numpy as np

import tensorflow as tf
import transformers #huggingface transformers library

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import sklearn
from sklearn.metrics import confusion_matrix
import os
import pickle

def _save_pickle(path, obj):
  with open(path, 'wb') as f:
    pickle.dump(obj, f)

def _load_pickle(path):
  with open(path, 'rb') as f:
    obj = pickle.load(f)
  return obj
  


class Predictor:
    
    def __init__(self):
        self.transformer = transformers.TFAutoModel.from_pretrained('modules/topic_classification/bert_model')
        self.tokenizer = _load_pickle("modules/topic_classification/tokenizer.pkl")
        self.encoder = _load_pickle("modules/topic_classification/encoder.pkl")
        self.encoded_classes = self.encoder.classes_
        self.build_model(max_len=80)
        
    def regular_encode(self, texts, maxlen=512):
        enc_di = self.tokenizer.batch_encode_plus(
            texts, 
            return_attention_mask =False, 
            return_token_type_ids=False,
            pad_to_max_length=True,
            max_length=maxlen
        )
        return np.array(enc_di['input_ids'])
    
        
    def predict(self, input_seq):
        test_encoded = self.regular_encode([input_seq], maxlen=80)
        pred = self.model.predict([test_encoded])
        pred_classes = np.argmax(pred, axis = 1)
        predicted_category = [self.encoded_classes[x] for x in pred_classes]
        return predicted_category[0]
    
    def build_model(self, loss='categorical_crossentropy', max_len=512):
        input_word_ids = tf.keras.layers.Input(shape=(max_len,), dtype=tf.int32, name="input_word_ids")
        sequence_output = self.transformer(input_word_ids)[0]
        cls_token = sequence_output[:, 0, :]
        #adding dropout layer
        x = tf.keras.layers.Dropout(0.3)(cls_token)
        #using a dense layer of 15 neurons as the number of unique categories is 40. 
        out = tf.keras.layers.Dense(16, activation='softmax')(x)
        self.model = tf.keras.Model(inputs=input_word_ids, outputs=out)
        #using categorical crossentropy as the loss as it is a multi-class classification problem
        self.model.compile(tf.keras.optimizers.Adam(lr=3e-5), loss=loss, metrics=['accuracy'])
        
        self.model.load_weights("modules/topic_classification/weights/model_weights.h5")
        
        
if __name__ == "__main__":
    predictor = Predictor()
    test = "Large companies have big budgets for marketing and promotion and as a result, people gravitate towards buying their products."
    print(predictor.predict(test))