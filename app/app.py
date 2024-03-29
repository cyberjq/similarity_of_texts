from app.methods.word_2_vec import W2V
from app.tools.doc_reader import DocReader
from app.tools.docx_tools import DocExecuter
from app.tools.plot import Plot
from app.tools.simmilatity_docs import SimilarityDocs
from app.tools.text_preprocessing import TextPreprocessing
from typing import List

class App:

    def __init__(self):
        self.w2v = W2V()
        self.text_preprocessing = TextPreprocessing()
        self.doc_reader = DocReader()
        self.doc_executer = DocExecuter()
        self.similarity_docs = SimilarityDocs(self.w2v)

    def read_data(self, dir, save_json_file: str = "data.json"):
        files = []
        for index, doc in enumerate(self.doc_reader.read_files(dir)):
            texts = self.doc_executer.execute_text(doc["file"], split_cell=False, split_paragraphs=True)
            filter_texts, texts = self.text_preprocessing.get_filter_documents(texts, is_sentences=True)

            files.append({
                "index": index,
                "file_name": doc["file_name"],
                "texts": texts,
                "filter_texts": filter_texts
            })

        if save_json_file:
            self.doc_reader.save_json(files, save_json_file)

        return files

    def read_json(self, path: str = "data.json"):
        return self.doc_reader.read_json(path)

    def train(self, files: List[dict], model_name: str):
        documents = [filter_text[1] for file in files for filter_text in file["filter_texts"]]
        self.w2v.train(documents, model_name=model_name, save=True)

    def run(self, is_read_data: bool = False, is_train: bool = False):
        dir = "data\original"
        params = "sentences_del_number_v2_vs300_w10_sg1_epochs30_negative10_min_count0"
        model_name = f"word2vec_{params}.model"

        files = self.read_data(dir, save_json_file="") \
            if is_read_data else self.read_json(path="sentences_data_del_number.json")

        self.train(files=files, model_name=model_name) if is_train else self.w2v.load(model_name)

        sims = self.similarity_docs.similarity(source_files=files, target_files=files)
        plot = Plot()
        plot.show_word_embeding(*self.w2v.reduce_dimensions(), file_name=f"wv_{params}.png")
        plot.show_heatmap(dataframe=sims, file_name=f"res_{params}_all.png", title="Сравнение документов",
                          cmap='coolwarm', figsize=(32, 32))