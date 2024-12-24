import os
import pickle
from typing import Any, Dict

import pandas as pd
import pyterrier as pt
from datasets import load_dataset
from sentence_transformers import CrossEncoder

from app.utils.query import QueryProcessor


class ModelManager:
    def __init__(self):
        self.cutoff = 30
        self.pipeline = None
        self.index = None
        self.dataframe = None
        self.env = (os.getenv('LOCAL_DEVELOPMENT', 'False') == 'True')

    def get_data_dir(self) -> str:
        if self.env:
            return os.path.join(os.path.abspath(os.curdir), "storage")
        else:
            return os.path.join('/tmp', 'downloads')

    def load_pipeline(self, config):
        bm25 = pt.BatchRetrieve(self.index, wmodel="BM25")

        crossmodel = CrossEncoder(
            config['components']['cross_encoder']['model_name'],
            max_length=config['components']['cross_encoder']['max_length']
        )

        def _crossencoder_apply(dataframe):
            return crossmodel.predict(
                list(zip(dataframe['query_raw'].values,
                     dataframe['text_raw'].values))
            )

        cross_encT = pt.apply.doc_score(_crossencoder_apply, batch_size=128)

        pipeline = (
            bm25 % self.cutoff
            >> pt.text.get_text(self.index, "text_raw")
            >> cross_encT
        )

        return pipeline

    async def load_dataset(self):
        ds = load_dataset("mteb/trec-covid", "corpus")
        corpus_df = pd.DataFrame(ds["corpus"])

        self.dataframe = corpus_df

    async def load_models(self):
        if not pt.started():
            pt.init()

        data_dir = self.get_data_dir()

        config_path = os.path.join(data_dir, "config.pkl")
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"Config file not found at {config_path}")

        print(f"Loading config from: {config_path}")
        with open(config_path, 'rb') as f:
            loaded_components = pickle.load(f)

        index_path = os.path.join(data_dir, "index/pyterrier")
        if not os.path.exists(index_path):
            raise FileNotFoundError(f"Index not found at {index_path}")

        print(f"Loading index from: {index_path}")

        self.cutoff = loaded_components['cut_off']
        self.index = pt.IndexFactory.of(index_path)
        self.pipeline = self.load_pipeline(loaded_components)

    async def cleanup(self):
        self.pipeline = None
        self.index = None

    def is_ready(self) -> bool:
        return self.pipeline is not None and self.pipeline is not None

    async def search(self, query: str) -> Dict[str, Any]:
        if not self.is_ready():
            raise RuntimeError("Models not loaded")

        query_processor = QueryProcessor()

        query = pd.DataFrame(
            [{"qid": "q1",  "query": query_processor.preprocessed_query(query), "query_raw": query}])

        results = self.pipeline.transform(query)

        merged_results = results.merge(
            self.dataframe, left_on="docno", right_on="_id", how="left")

        return merged_results[["title", "text"]].to_dict('records')
