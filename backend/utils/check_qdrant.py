import os
import sys
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

def check_qdrant_data():
    """检查 Qdrant 数据库中的数据"""
    try:
        # 初始化 Qdrant 客户端
        qdrant_client = QdrantClient(
            path="/Users/nuoyunzhibo/xu/project/LLM/Agent-zy/local_qdrant"
        )

        # 获取集合信息
        collections = qdrant_client.get_collections().collections
        print(f"找到 {len(collections)} 个集合")

        for collection in collections:
            collection_name = collection.name
            print(f"\n检查集合: {collection_name}")

            # 获取集合的详细信息
            collection_info = qdrant_client.get_collection(collection_name)
            print(f"向量维度: {collection_info.config.params.vectors.size}")
            print(f"距离度量: {collection_info.config.params.vectors.distance}")

            # 获取集合中的点数量
            points_count = qdrant_client.count(collection_name)
            print(f"文档数量: {points_count.count}")

            # 获取一些示例文档
            if points_count.count > 0:
                print("\n示例文档:")
                points = qdrant_client.scroll(
                    collection_name=collection_name,
                    limit=5,  # 只显示前5个文档
                    with_vectors=True  # 确保返回向量
                )[0]

                for point in points:
                    print(f"\n文档ID: {point.id}")
                    if point.vector is not None:
                        print(f"向量维度: {len(point.vector)}")
                    else:
                        print("向量: None")
                    print(f"元数据: {point.payload}")
                    print("-" * 50)

    except Exception as e:
        print(f"检查 Qdrant 数据时出错: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    check_qdrant_data()