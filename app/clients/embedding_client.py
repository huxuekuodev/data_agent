from dataclasses import dataclass
from typing import List

from langchain_core.embeddings import Embeddings
from ollama import Client  # 确保你安装了 ollama 库

from app.conf.app_config import EmbeddingConfig


@dataclass
class OllamaEmbedding(Embeddings):

    embed_config: EmbeddingConfig

    def __post_init__(self):
        """
        初始化 Ollama 嵌入模型
        :param model_name: 默认使用的嵌入模型名称
        :param dimensions: 嵌入向量的维度（Qwen3 默认支持多维度，1024 是常见高性能选择）
        """
        self.client = Client(
            host=f"http://{self.embed_config.host}:{self.embed_config.port}"
        )
        self.model_name = self.embed_config.model
        self.dimensions = self.embed_config.dimensions

    def get_embeddings(self, inpt: List[str]) -> List[List[float]]:
        """
        底层的批量获取嵌入向量方法
        """
        try:
            emb_resp = self.client.embed(
                model=self.model_name, dimensions=self.dimensions, input=inpt
            )
            return emb_resp.embeddings
        except Exception as e:
            # 生产环境增加异常捕获
            raise RuntimeError(f"Ollama 嵌入服务调用失败: {str(e)}")

    def embed_query(self, text: str) -> List[float]:
        """
        实现 LangChain 接口：为单个查询（提问）生成向量
        """
        # 即使是单个文本，Ollama 接口也需要包裹成 list 传进去，拿到结果后取第 0 个
        embeddings = self.get_embeddings([text])
        return embeddings[0]

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        实现 LangChain 接口：为批量文档生成向量
        """
        if not texts:
            return []
        return self.get_embeddings(texts)
