from dataclasses import dataclass
from typing import List

import requests

# 引入 LangChain 的标准嵌入基类
from langchain_core.embeddings import Embeddings

from app.conf.app_config import SiliconFlowEmbeddingConfig, app_config


class PureRequestsEmbeddings(Embeddings):
    """
    使用纯 requests 实现的硅基流动 Embedding 客户端
    严格遵循官方最小参数集，彻底杜绝 400 报错，完美支持批量
    """

    def __init__(self, model: str, api_key: str, base_url: str):
        self.model = model
        self.api_key = api_key
        # 确保 base_url 最终指向 /embeddings 终点
        self.api_url = f"{base_url.rstrip('/')}/embeddings"
        self.headers = {
            "Authorization": (
                f"Base {self.api_key}"
                if "Bearer" in self.api_key
                else f"Bearer {self.api_key}"
            ),
            "Content-Type": "application/json",
        }

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        批量请求接口 (支持传入多个文本的列表)
        """
        payload = {"input": texts, "model": self.model}

        response = requests.post(self.api_url, headers=self.headers, json=payload)

        # 抛出 HTTP 错误（如 401, 404, 500 等）
        response.raise_for_status()

        res_json = response.json()

        # 解析硅基流动返回的标准 Embedding 结构
        # 按照 data 里的 index 排序，确保返回顺序与输入完全一致
        sorted_data = sorted(res_json["data"], key=lambda x: x["index"])
        return [item["embedding"] for item in sorted_data]

    def embed_query(self, text: str) -> List[float]:
        """
        单条请求接口 (内部直接复用批量接口)
        """
        return self.embed_documents([text])[0]


@dataclass
class SiliconFlowEmbeddingClient:
    """
    硅光流嵌入客户端
    """

    config: SiliconFlowEmbeddingConfig
    embeddings: PureRequestsEmbeddings = None  # 替换为我们自定义的纯净请求类

    def __post_init__(self):
        self.embeddings = PureRequestsEmbeddings(
            model=self.config.model,
            api_key=self.config.token,
            base_url=self.config.base_url,
        )


siliconFlowEmbeddingClient = SiliconFlowEmbeddingClient(
    config=app_config.siliconFlow_embedding
)

if __name__ == "__main__":
    # ---- 测试 1：单条文本查询 ----
    print("--- 正在测试单条查询 ---")
    query_res = siliconFlowEmbeddingClient.embeddings.embed_query("你好")
    print(f"单条向量长度: {len(query_res)}")
    print(f"前5维数据: {query_res[:5]}\n")

    # ---- 测试 2：批量文本查询 (支持 List[str]) ----
    print("--- 正在测试批量查询 ---")
    batch_texts = ["你好", "很高兴认识你", "再见"]
    batch_res = siliconFlowEmbeddingClient.embeddings.embed_documents(batch_texts)
    print(f"批量返回条数: {len(batch_res)}")
    for i, emb in enumerate(batch_res):
        print(f"文本 '{batch_texts[i]}' 的向量维度: {len(emb)}, 前3维: {emb[:3]}")
