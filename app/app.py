from app.methods.word_2_vec import W2V
from app.tools.doc_reader import DocReader
from app.tools.docx_tools import DocExecuter
from app.tools.simmilatity_docs import SimilarityDocs
from app.tools.text_preprocessing import TextPreprocessing


class App:

    def __init__(self):
        self.w2v = W2V()
        self.text_preprocessing = TextPreprocessing()
        self.doc_reader = DocReader()
        self.doc_executer = DocExecuter()
        self.similarity_docs = SimilarityDocs(self.w2v)

    def read_data(self, dir):
        files = []
        for index, doc in enumerate(self.doc_reader.read_files(dir)):
            texts = self.doc_executer.execute_text(doc["file"], split_cell=False, split_paragraphs=True)
            filter_texts = self.text_preprocessing.get_filter_documents(texts, is_paragraph=True)[0]

            files.append({
                "index": index,
                "file_name": doc["file_name"],
                "texts": texts,
                "filter_texts": filter_texts
            })

        self.doc_reader.save_json(files, "data.json")
        return files

    def read_json(self, path: str = "data.json"):
        return self.doc_reader.read_json(path)

    def train(self, dir: str, model_name: str):
        documents = []
        for doc in self.doc_reader.read_files(dir):
            texts = self.doc_executer.execute_text(doc, split_cell=False, split_paragraphs=True)
            documents.extend(self.text_preprocessing.get_filter_documents(texts, is_paragraph=True)[0])

            # documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(documents)]

        self.w2v.train(documents)
        self.w2v.save(model_name)

    def run(self, is_read_data: bool = False, is_train: bool = False):
        dir = "data\cleaned"
        model_name = "word2vec.model"

        files = self.read_data(dir) if is_read_data else self.read_json()
        self.train(dir=dir, model_name=model_name) if is_train else self.w2v.load(model_name)

        source_file = files[0]
        target_files = list(filter(lambda x: x["file_name"] != source_file["file_name"], files))

        self.similarity_docs.similarity(source_file, target_files)