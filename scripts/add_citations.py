"""
添加论文引用关系数据
"""
from neo4j import GraphDatabase, basic_auth
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# Neo4j 连接配置
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "YOUR_NEO4J_PASSWORD")

def add_citation_relationships():
    """添加论文引用关系"""
    print(f"尝试连接到 Neo4j: {NEO4J_URI}")
    print(f"用户名: {NEO4J_USER}")

    try:
        driver = GraphDatabase.driver(NEO4J_URI, auth=basic_auth(NEO4J_USER, NEO4J_PASSWORD))
        # 验证连接
        driver.verify_connectivity()
        print("成功连接到 Neo4j 数据库")
    except Exception as e:
        print(f"连接 Neo4j 失败: {e}")
        print("请检查：")
        print("1. Neo4j 服务是否已启动")
        print("2. .env 文件中的 NEO4J_URI、NEO4J_USER、NEO4J_PASSWORD 是否正确")
        return

    with driver.session() as session:
        # 1. 获取所有论文节点
        print("正在查询论文节点...")
        result = session.run("MATCH (p:Paper) RETURN p.id AS paper_id, p.title AS title LIMIT 30")
        papers = [{"id": record["paper_id"], "title": record["title"]} for record in result]

        if len(papers) < 2:
            print("至少需要2篇论文才能创建引用关系")
            return

        print(f"找到 {len(papers)} 篇论文，正在创建引用关系...")

        # 2. 创建示例引用关系（简单模式：论文i引用论文i+1）
        for i in range(len(papers) - 1):
            paper1 = papers[i]
            paper2 = papers[i + 1]

            # 创建引用关系
            session.run("""
                MATCH (p1:Paper {id: $paper1_id}), (p2:Paper {id: $paper2_id})
                MERGE (p1)-[r:CITES]->(p2)
                ON CREATE SET r.citation_count = 1, r.year = 2023
                ON MATCH SET r.citation_count = r.citation_count + 1
                RETURN r
            """, paper1_id=paper1["id"], paper2_id=paper2["id"])

            print(f"创建引用关系: {paper1['title']} -> {paper2['title']}")

        # 3. 创建一些交叉引用
        if len(papers) >= 5:
            # 第0篇引用第3篇
            session.run("""
                MATCH (p1:Paper {id: $paper1_id}), (p2:Paper {id: $paper2_id})
                MERGE (p1)-[r:CITES]->(p2)
                ON CREATE SET r.citation_count = 1, r.year = 2022
                ON MATCH SET r.citation_count = r.citation_count + 1
                RETURN r
            """, paper1_id=papers[0]["id"], paper2_id=papers[3]["id"])
            print(f"创建交叉引用: {papers[0]['title']} -> {papers[3]['title']}")

            # 第4篇引用第1篇
            session.run("""
                MATCH (p1:Paper {id: $paper1_id}), (p2:Paper {id: $paper2_id})
                MERGE (p1)-[r:CITES]->(p2)
                ON CREATE SET r.citation_count = 1, r.year = 2021
                ON MATCH SET r.citation_count = r.citation_count + 1
                RETURN r
            """, paper1_id=papers[4]["id"], paper2_id=papers[1]["id"])
            print(f"创建交叉引用: {papers[4]['title']} -> {papers[1]['title']}")

    driver.close()
    print("引用关系创建完成!")

if __name__ == "__main__":
    add_citation_relationships()
