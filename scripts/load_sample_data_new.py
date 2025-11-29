"""加载示例数据"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, neo4j_conn
from app.models.mysql_models import PaperInfo, AuthorInfo, OrganizationInfo, PaperAuthorRelation
from app.repositories.neo4j_dao import GraphDAO
from loguru import logger
import random
from faker import Faker
fake = Faker(["en_US", "zh_CN"])

def load_sample_data():
    db = SessionLocal()
    
    try:
        logger.info("开始加载示例数据...")

        # ================================
        # 1. 组织（10 个）
        # ================================
        orgs = []
        org_names = [
            ("清华大学", "中国", "THU"),
            ("北京大学", "中国", "PKU"),
            ("浙江大学", "中国", "ZJU"),
            ("中国科学院大学", "中国", "UCAS"),
            ("复旦大学", "中国", "FDU"),
            ("Stanford University", "USA", "Stanford"),
            ("MIT", "USA", "MIT"),
            ("Carnegie Mellon University", "USA", "CMU"),
            ("University of Oxford", "UK", "Oxford"),
            ("University of Tokyo", "Japan", "UTokyo")
        ]

        for i, (name, country, abbr) in enumerate(org_names, start=1):
            orgs.append({
                "org_id": f"org_{i:03d}",
                "name": name,
                "country": country,
                "abbreviation": abbr,
                "rank_score": round(random.uniform(80, 100), 2),
                "paper_count": 0
            })

        for org_data in orgs:
            db.merge(OrganizationInfo(**org_data))
        db.commit()
        logger.info(f"✓ 创建了 {len(orgs)} 个单位")

        # ================================
        # 2. 作者（30 个）
        # ================================
        authors = []
        for i in range(1, 31):
            authors.append({
                "author_id": f"author_{i:03d}",
                "name": fake.name(),
                "org_id": f"org_{random.randint(1, 10):03d}",
                "h_index": random.randint(5, 70),
                "paper_count": 0,
                "orcid": f"0000-000{random.randint(1000,9999)}-{random.randint(1000,9999)}",
                "email": fake.email()
            })

        for author_data in authors:
            db.merge(AuthorInfo(**author_data))
        db.commit()
        logger.info(f"✓ 创建了 {len(authors)} 个作者")

        # ================================
        # 3. 论文（50 篇）
        # ================================
        venues = ["AAAI 2023", "ACL 2022", "KDD 2023", "ICML 2023", "NeurIPS 2022",
                  "EMNLP 2023", "WWW 2023", "SIGIR 2022", "IJCAI 2023"]

        keywords_pool = ["深度学习", "图神经网络", "知识图谱", "自然语言处理", "大模型",
                         "机器翻译", "强化学习", "表示学习", "元学习"]

        papers = []
        for i in range(1, 51):
            papers.append({
                "paper_id": f"paper_{i:03d}",
                "title": fake.sentence(nb_words=6),
                "abstract": fake.text(max_nb_chars=150),
                "year": random.randint(2018, 2024),
                "venue": random.choice(venues),
                "doi": f"10.1000/{fake.pyint()}",
                "keywords": ";".join(random.sample(keywords_pool, k=3)),
                "url": fake.url(),
                "citation_count": random.randint(0, 200)
            })

        for paper_data in papers:
            db.merge(PaperInfo(**paper_data))
        db.commit()
        logger.info(f"✓ 创建了 {len(papers)} 篇论文")

        # ================================
        # 4. 论文-作者关系（随机 120~150 个）
        # ================================
        relations = []
        for p in papers:
            paper_id = p["paper_id"]

            # 每篇论文 2～4 个作者
            num_auth = random.randint(2, 4)
            chosen_authors = random.sample(authors, num_auth)

            for order, auth in enumerate(chosen_authors, start=1):
                relations.append({
                    "paper_id": paper_id,
                    "author_id": auth["author_id"],
                    "author_order": order,
                    "is_corresponding": 1 if order == 1 else 0
                })

        for rel_data in relations:
            db.add(PaperAuthorRelation(**rel_data))
        db.commit()
        logger.info(f"✓ 创建了 {len(relations)} 个论文-作者关系")
        # ================================
        # 11/30 修正 paper_count
        # ================================
        for author in authors:
            count = db.query(PaperAuthorRelation).filter(
                PaperAuthorRelation.author_id == author["author_id"]
            ).count()
            db.query(AuthorInfo).filter(AuthorInfo.author_id == author["author_id"]).update(
                {"paper_count": count}
            )
        for org in orgs:
            count = db.query(PaperInfo)\
                .join(PaperAuthorRelation, PaperInfo.paper_id == PaperAuthorRelation.paper_id)\
                .join(AuthorInfo, PaperAuthorRelation.author_id == AuthorInfo.author_id)\
                .filter(AuthorInfo.org_id == org["org_id"]).count()
            db.query(OrganizationInfo).filter(OrganizationInfo.org_id == org["org_id"]).update(
                {"paper_count": count}
            )
        db.commit()
        logger.info("✓ 更新作者和机构的论文数量")
        # ================================
        # 5. 同步 Neo4j
        # ================================
        logger.info("开始同步数据到 Neo4j...")
        sync_to_neo4j(db)

        logger.info("✓ 示例数据加载完成！")

    except Exception as e:
        logger.error(f"✗ 加载示例数据失败: {e}")
        db.rollback()
        raise

    finally:
        db.close()

def sync_to_neo4j(db):
    try:
        driver = neo4j_conn.get_driver()
        dao = GraphDAO(driver)
        
        with driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("✓ 清空 Neo4j 现有数据")
            
            orgs = db.query(OrganizationInfo).all()
            org_node_map = {}
            for org in orgs:
                node_id = dao.create_organization_node({
                    "id": org.org_id,
                    "name": org.name,
                    "country": org.country,
                    "abbreviation": org.abbreviation,
                    "rank_score": float(org.rank_score) if org.rank_score else 0
                })
                org_node_map[org.org_id] = node_id
            logger.info(f"✓ 同步了 {len(orgs)} 个组织节点")
            
            authors = db.query(AuthorInfo).all()
            author_node_map = {}
            for author in authors:
                node_id = dao.create_author_node({
                    "id": author.author_id,
                    "name": author.name,
                    "h_index": author.h_index,
                    "orcid": author.orcid,
                    "email": author.email
                })
                author_node_map[author.author_id] = node_id
                
                if author.org_id and author.org_id in org_node_map:
                    dao.create_relationship(node_id, org_node_map[author.org_id], "AFFILIATED_WITH")
            logger.info(f"✓ 同步了 {len(authors)} 个作者节点")
            
            papers = db.query(PaperInfo).all()
            paper_node_map = {}
            for paper in papers:
                node_id = dao.create_paper_node({
                    "id": paper.paper_id,
                    "title": paper.title,
                    "year": paper.year,
                    "venue": paper.venue,
                    "doi": paper.doi,
                    "keywords": paper.keywords,
                    "citation_count": paper.citation_count
                })
                paper_node_map[paper.paper_id] = node_id
            logger.info(f"✓ 同步了 {len(papers)} 个论文节点")
            
            relations = db.query(PaperAuthorRelation).all()
            for rel in relations:
                if rel.author_id in author_node_map and rel.paper_id in paper_node_map:
                    dao.create_relationship(
                        author_node_map[rel.author_id],
                        paper_node_map[rel.paper_id],
                        "AUTHORED",
                        {"order": rel.author_order, "is_corresponding": rel.is_corresponding}
                    )
            logger.info(f"✓ 同步了 {len(relations)} 个作者-论文关系")
            
            session.close()
        
    except Exception as e:
        logger.error(f"✗ 同步到 Neo4j 失败: {e}")
        raise

def main():
    logger.info("=" * 60)
    logger.info("论文知识图谱系统 - 加载示例数据")
    logger.info("=" * 60)
    
    try:
        load_sample_data()
        logger.info("=" * 60)
        logger.info("示例数据加载成功！")
        logger.info("=" * 60)
        return 0
    except Exception as e:
        logger.error(f"加载失败: {e}")
        return 1

if __name__ == "__main__":
    exit(main())