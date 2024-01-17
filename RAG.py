import pandas as pd

from datasets import load_dataset

from langchain import PromptTemplate, LLMChain
from langchain.llms import GPT4All
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain import PromptTemplate
from langchain.document_loaders import TextLoader
from langchain import PromptTemplate
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

from langchain.document_loaders import TextLoader
from langchain.indexes import VectorstoreIndexCreator
from langchain.embeddings import HuggingFaceEmbeddings

dataset = load_dataset('medical_dialog', 'processed.en')
df = pd.DataFrame(dataset['train'])

dialog = []

# 患者と医者の発言をそれぞれ抽出した後、順にリストに格納
patient, doctor = zip(*df['utterances'])
for i in range(len(patient)):
  dialog.append(patient[i])
  dialog.append(doctor[i])

df_dialog = pd.DataFrame({"dialog": dialog})

# 成形終了したデータセットを保存
df_dialog.to_csv('medical_data.txt', sep=' ', index=False)

loader = TextLoader('medical_data.txt', encoding="utf-8")
index = VectorstoreIndexCreator(embedding= HuggingFaceEmbeddings()).from_loaders([loader])
