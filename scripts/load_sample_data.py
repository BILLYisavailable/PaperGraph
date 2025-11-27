"""加载示例数据"""
import sys, os
import random
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, neo4j_conn, redis_conn
from app.models.mysql_models import PaperInfo, AuthorInfo, OrganizationInfo, PaperAuthorRelation
from app.repositories.neo4j_dao import GraphDAO
from app.services.graph_service import GraphService
from app.services.statistics_service import StatisticsService
from app.repositories.mysql_dao import StatisticsDAO
from loguru import logger

# 10所高校配置
UNIVERSITIES = [
    {"name": "清华大学", "country": "中国", "abbreviation": "THU", "rank_score": 98.5},
    {"name": "北京大学", "country": "中国", "abbreviation": "PKU", "rank_score": 97.8},
    {"name": "复旦大学", "country": "中国", "abbreviation": "FDU", "rank_score": 96.2},
    {"name": "上海交通大学", "country": "中国", "abbreviation": "SJTU", "rank_score": 95.8},
    {"name": "浙江大学", "country": "中国", "abbreviation": "ZJU", "rank_score": 95.5},
    {"name": "MIT", "country": "美国", "abbreviation": "MIT", "rank_score": 99.5},
    {"name": "Stanford University", "country": "美国", "abbreviation": "Stanford", "rank_score": 99.2},
    {"name": "Harvard University", "country": "美国", "abbreviation": "Harvard", "rank_score": 99.8},
    {"name": "Oxford University", "country": "英国", "abbreviation": "Oxford", "rank_score": 98.9},
    {"name": "Cambridge University", "country": "英国", "abbreviation": "Cambridge", "rank_score": 98.7},
]

# 中文姓氏和名字
CHINESE_SURNAMES = ["张", "王", "李", "刘", "陈", "杨", "赵", "黄", "周", "吴", "徐", "孙", "胡", "朱", "高", "林", "何", "郭", "马", "罗"]
CHINESE_GIVEN_NAMES = ["伟", "芳", "娜", "秀英", "敏", "静", "丽", "强", "磊", "军", "洋", "勇", "艳", "杰", "华", "明", "刚", "平", "辉", "鹏"]

# 英文名字
ENGLISH_FIRST_NAMES = ["James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
                       "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen"]
ENGLISH_LAST_NAMES = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
                      "Wilson", "Anderson", "Taylor", "Thomas", "Hernandez", "Moore", "Martin", "Jackson", "Thompson", "White"]

# 论文标题模板
PAPER_TITLE_TEMPLATES = [
    "Advanced Research on {topic}",
    "Novel Approaches to {topic}",
    "Deep Learning Applications in {topic}",
    "Machine Learning Methods for {topic}",
    "A Comprehensive Study of {topic}",
    "Recent Advances in {topic}",
    "Optimization Techniques for {topic}",
    "Data Mining and {topic}",
    "Neural Network Architectures for {topic}",
    "Statistical Analysis of {topic}",
]

# 研究主题
RESEARCH_TOPICS = [
    "Knowledge Graph Construction", "Natural Language Processing", "Computer Vision",
    "Reinforcement Learning", "Graph Neural Networks", "Data Mining",
    "Information Retrieval", "Machine Translation", "Sentiment Analysis",
    "Recommendation Systems", "Network Analysis", "Distributed Systems",
    "Cloud Computing", "Cybersecurity", "Blockchain Technology",
    "Quantum Computing", "Bioinformatics", "Computational Biology",
    "Robotics", "Autonomous Vehicles", "IoT Systems", "Edge Computing"
]

# 会议/期刊
VENUES = [
    "AAAI", "ICML", "NeurIPS", "ICLR", "KDD", "SIGIR", "ACL", "EMNLP",
    "CVPR", "ICCV", "ECCV", "WWW", "SIGMOD", "VLDB", "ICDE", "ICDCS",
    "Nature", "Science", "Cell", "PNAS", "IEEE TPAMI", "JMLR"
]

YEARS = [2020, 2021, 2022, 2023, 2024]

def generate_author_name(org_country, author_index):
    """根据组织国家生成作者姓名"""
    if org_country == "中国":
        surname = CHINESE_SURNAMES[author_index % len(CHINESE_SURNAMES)]
        given_name = CHINESE_GIVEN_NAMES[(author_index // len(CHINESE_SURNAMES)) % len(CHINESE_GIVEN_NAMES)]
        return f"{surname}{given_name}"
    else:
        first_name = ENGLISH_FIRST_NAMES[author_index % len(ENGLISH_FIRST_NAMES)]
        last_name = ENGLISH_LAST_NAMES[(author_index // len(ENGLISH_FIRST_NAMES)) % len(ENGLISH_LAST_NAMES)]
        return f"{first_name} {last_name}"

def generate_paper_title(paper_index):
    """生成论文标题"""
    topic = RESEARCH_TOPICS[paper_index % len(RESEARCH_TOPICS)]
    template = PAPER_TITLE_TEMPLATES[paper_index % len(PAPER_TITLE_TEMPLATES)]
    return template.format(topic=topic)

def generate_keywords(paper_index):
    """生成关键词"""
    topics = random.sample(RESEARCH_TOPICS, min(3, len(RESEARCH_TOPICS)))
    return ";".join(topics)

def load_sample_data():
    db = SessionLocal()
    
    try:
        logger.info("开始加载示例数据...")
        logger.info("数据规模: 10所高校 × 10名作者 × 10篇文章 = 1000篇文章")
        
        # 0. 清空现有数据（按外键依赖顺序删除）
        logger.info("正在清空现有数据...")
        logger.info("Clearing existing data...")
        
        # 先删除关系表（有外键约束）
        db.query(PaperAuthorRelation).delete()
        logger.info("✓ 已清空论文-作者关系表")
        
        # 再删除主表
        db.query(PaperInfo).delete()
        logger.info("✓ 已清空论文表")
        
        db.query(AuthorInfo).delete()
        logger.info("✓ 已清空作者表")
        
        db.query(OrganizationInfo).delete()
        logger.info("✓ 已清空组织表")
        
        db.commit()
        logger.info("✓ MySQL 数据清空完成")
        logger.info("✓ MySQL data cleared")
        
        # 1. 创建10所高校
        orgs = []
        for i, uni_data in enumerate(UNIVERSITIES, 1):
            org_id = f"org_{i:03d}"
            org_data = {
                "org_id": org_id,
                "name": uni_data["name"],
                "country": uni_data["country"],
                "abbreviation": uni_data["abbreviation"],
                "rank_score": uni_data["rank_score"],
                "paper_count": 0
            }
            orgs.append(org_data)
            org = OrganizationInfo(**org_data)
            db.merge(org)
        
        db.commit()
        logger.info(f"✓ 创建了 {len(orgs)} 所高校")
        
        # 2. 为每所高校创建10名作者
        authors = []
        author_counter = 1
        for org in orgs:
            org_id = org["org_id"]
            org_country = org["country"]
            org_abbreviation = org["abbreviation"].lower()
            
            for j in range(10):
                author_id = f"author_{author_counter:04d}"
                author_name = generate_author_name(org_country, author_counter - 1)
                
                # 生成h_index (10-50之间)
                h_index = random.randint(10, 50)
                
                # 生成ORCID
                orcid = f"0000-000{random.randint(1,9)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}"
                
                # 生成邮箱
                if org_country == "中国":
                    email = f"{author_name.lower().replace(' ', '')}@{org_abbreviation}.edu.cn"
                else:
                    email = f"{author_name.lower().replace(' ', '.')}@{org_abbreviation}.edu"
                
                author_data = {
                    "author_id": author_id,
                    "name": author_name,
                    "org_id": org_id,
                    "h_index": h_index,
                    "paper_count": 0,
                    "orcid": orcid,
                    "email": email
                }
                authors.append(author_data)
                author_obj = AuthorInfo(**author_data)
                db.merge(author_obj)
                author_counter += 1
            
            # 每所高校的作者批量提交一次
            db.commit()
            logger.info(f"✓ {org['name']}: 创建了 10 名作者")
        
        logger.info(f"✓ 总共创建了 {len(authors)} 名作者")
        
        # 3. 为每个作者创建10篇文章
        papers = []
        relations = []
        paper_counter = 1
        
        for idx, author in enumerate(authors):
            author_id = author["author_id"]
            author_paper_ids = []  # 保存这个作者的所有论文ID
            
            # 先创建这个作者的所有论文
            for k in range(10):
                paper_id = f"paper_{paper_counter:05d}"
                author_paper_ids.append(paper_id)  # 保存paper_id
                paper_title = generate_paper_title(paper_counter - 1)
                
                # 生成年份
                year = random.choice(YEARS)
                
                # 生成会议/期刊
                venue = f"{random.choice(VENUES)} {year}"
                
                # 生成DOI
                doi = f"10.{random.randint(1000,9999)}/{random.choice(['aaai', 'icml', 'neurips', 'acl', 'kdd'])}.{year}.{random.randint(10000,99999)}"
                
                # 生成关键词
                keywords = generate_keywords(paper_counter - 1)
                
                # 生成摘要
                abstract = f"This paper presents a comprehensive study of {generate_paper_title(paper_counter - 1).lower()}. " \
                          f"We propose novel methods and conduct extensive experiments to demonstrate the effectiveness of our approach."
                
                # 生成引用数 (0-100之间)
                citation_count = random.randint(0, 100)
                
                # 生成URL
                url = f"https://example.com/paper/{paper_id}"
                
                paper_data = {
                    "paper_id": paper_id,
                    "title": paper_title,
                    "abstract": abstract,
                    "year": year,
                    "venue": venue,
                    "doi": doi,
                    "keywords": keywords,
                    "url": url,
                    "citation_count": citation_count
                }
                papers.append(paper_data)
                paper_obj = PaperInfo(**paper_data)
                db.merge(paper_obj)
                
                paper_counter += 1
            
            # 先flush确保所有论文都已插入数据库（满足外键约束）
            db.flush()
            
            # 然后为这个作者的所有论文创建关系
            for paper_id in author_paper_ids:
                # 创建论文-作者关系（每篇论文只有一个作者，该作者为第一作者和通讯作者）
                rel_data = {
                    "paper_id": paper_id,
                    "author_id": author_id,
                    "author_order": 1,
                    "is_corresponding": 1
                }
                relations.append(rel_data)
                rel_obj = PaperAuthorRelation(**rel_data)
                db.add(rel_obj)
            
            # 每完成一个作者的所有文章后提交一次（每10篇文章提交一次）
            db.commit()
            
            # 每10个作者显示一次进度
            if (idx + 1) % 10 == 0:
                logger.info(f"✓ 进度: {idx + 1}/{len(authors)} 名作者已完成 ({paper_counter - 1} 篇文章)")
        logger.info(f"✓ 总共创建了 {len(papers)} 篇论文")
        logger.info(f"✓ 总共创建了 {len(relations)} 个论文-作者关系")
        
        logger.info("开始同步数据到 Neo4j...")
        sync_to_neo4j(db)
        
        logger.info("正在清除Redis缓存...")
        logger.info("Clearing Redis cache...")
        clear_all_cache()
        
        logger.info("✓ 示例数据加载完成！")
        logger.info(f"   - 高校: {len(orgs)} 所")
        logger.info(f"   - 作者: {len(authors)} 名")
        logger.info(f"   - 论文: {len(papers)} 篇")
        logger.info(f"   - 关系: {len(relations)} 个")
        
    except Exception as e:
        logger.error(f"✗ 加载示例数据失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        db.rollback()
        raise
    
    finally:
        db.close()

def clear_all_cache():
    """清除所有Redis缓存"""
    try:
        redis_client = redis_conn.get_client()
        if not redis_client:
            logger.warning("Redis客户端不可用，跳过缓存清除")
            return
        
        # 清除图谱相关缓存
        graph_patterns = ["graph:root:*", "graph:children:*", "graph:node:*"]
        graph_deleted = 0
        for pattern in graph_patterns:
            keys = redis_client.keys(pattern)
            if keys:
                deleted = redis_client.delete(*keys)
                graph_deleted += deleted if isinstance(deleted, int) else len(keys)
        
        # 清除统计相关缓存
        stat_keys = redis_client.keys("stat:*")
        stat_deleted = 0
        if stat_keys:
            deleted = redis_client.delete(*stat_keys)
            stat_deleted = deleted if isinstance(deleted, int) else len(stat_keys)
        
        total_deleted = graph_deleted + stat_deleted
        if total_deleted > 0:
            logger.info(f"✓ 清除了 {total_deleted} 个缓存项（图谱: {graph_deleted}, 统计: {stat_deleted}）")
        else:
            logger.info("✓ 没有需要清除的缓存")
    except Exception as e:
        logger.warning(f"清除缓存失败: {e}")

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

