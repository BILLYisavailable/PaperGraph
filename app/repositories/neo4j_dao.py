"""
Neo4j 数据访问对象
"""
from typing import List, Dict, Any, Tuple, Optional
from neo4j import Session
from loguru import logger


class GraphDAO:
    """图数据库访问类"""
    
    def __init__(self, driver):
        self.driver = driver
    
    def query_root(self, params: Dict[str, Any]) -> Tuple[List[Dict], List[Dict]]:
        """
        查询根节点图谱数据
        
        Args:
            params: 查询参数，如 {"limit": 100}
            
        Returns:
            (nodes, edges) 节点列表和边列表
        """
        limit = params.get("limit", 100)
        
        query = """
        MATCH (a:Author)-[r1:AUTHORED]->(p:Paper)
        OPTIONAL MATCH (a)-[r2:AFFILIATED_WITH]->(o:Organization)
        WITH a, p, o, r1, r2
        LIMIT $limit
        RETURN a, p, o, r1, r2
        """
        with self.driver.session() as session:
            try:
                result = session.run(query, limit=limit)
                nodes = []
                edges = []
                node_ids = set()
                
                for record in result:
                    # 处理作者节点
                    if record["a"]:
                        author = record["a"]
                        author_id = str(author.id)
                        if author_id not in node_ids:
                            nodes.append({
                                "id": author_id,
                                "label": "Author",
                                "properties": dict(author)
                            })
                            node_ids.add(author_id)
                    
                    # 处理论文节点
                    if record["p"]:
                        paper = record["p"]
                        paper_id = str(paper.id)
                        if paper_id not in node_ids:
                            nodes.append({
                                "id": paper_id,
                                "label": "Paper",
                                "properties": dict(paper)
                            })
                            node_ids.add(paper_id)
                    
                    # 处理单位节点
                    if record["o"]:
                        org = record["o"]
                        org_id = str(org.id)
                        if org_id not in node_ids:
                            nodes.append({
                                "id": org_id,
                                "label": "Organization",
                                "properties": dict(org)
                            })
                            node_ids.add(org_id)
                    
                    # 处理关系
                    if record["r1"]:
                        rel = record["r1"]
                        edges.append({
                            "id": str(rel.id),
                            "source": str(rel.start_node.id),
                            "target": str(rel.end_node.id),
                            "type": rel.type,
                            "properties": dict(rel)
                        })
                    
                    if record["r2"]:
                        rel = record["r2"]
                        edges.append({
                            "id": str(rel.id),
                            "source": str(rel.start_node.id),
                            "target": str(rel.end_node.id),
                            "type": rel.type,
                            "properties": dict(rel)
                        })
                
                return nodes, edges
            
            except Exception as e:
                logger.error(f"查询根节点失败: {e}")
                raise
    
    def query_children(self, node_id: str) -> Tuple[List[Dict], List[Dict]]:
        """
        查询指定节点的子节点
        
        Args:
            node_id: 节点ID
            
        Returns:
            (nodes, edges) 节点列表和边列表
        """
        query = """
        MATCH (n)-[r]-(m)
        WHERE id(n) = $node_id
        RETURN n, r, m
        """
        with self.driver.session() as session:
            try:
                result = session.run(query, node_id=int(node_id))
                nodes = []
                edges = []
                node_ids = set()
                
                for record in result:
                    # 中心节点
                    if record["n"]:
                        node = record["n"]
                        nid = str(node.id)
                        if nid not in node_ids:
                            nodes.append({
                                "id": nid,
                                "label": list(node.labels)[0] if node.labels else "Node",
                                "properties": dict(node)
                            })
                            node_ids.add(nid)
                    
                    # 相关节点
                    if record["m"]:
                        node = record["m"]
                        nid = str(node.id)
                        if nid not in node_ids:
                            nodes.append({
                                "id": nid,
                                "label": list(node.labels)[0] if node.labels else "Node",
                                "properties": dict(node)
                            })
                            node_ids.add(nid)
                    
                    # 关系
                    if record["r"]:
                        rel = record["r"]
                        edges.append({
                            "id": str(rel.id),
                            "source": str(rel.start_node.id),
                            "target": str(rel.end_node.id),
                            "type": rel.type,
                            "properties": dict(rel)
                        })
                
                return nodes, edges
            
            except Exception as e:
                logger.error(f"查询子节点失败: {e}")
                raise
        
    def query_node_info(self, node_id: str) -> Optional[Dict[str, Any]]:
        """
        查询节点详细信息
        
        Args:
            node_id: 节点ID
            
        Returns:
            节点信息字典
        """
        query = """
        MATCH (n)
        WHERE id(n) = $node_id
        RETURN n, labels(n) as labels
        """
        with self.driver.session() as session:
            try:
                result = session.run(query, node_id=int(node_id))
                record = result.single()
                
                if record:
                    node = record["n"]
                    return {
                        "id": str(node.id),
                        "label": record["labels"][0] if record["labels"] else "Node",
                        "properties": dict(node)
                    }
                return None
            
            except Exception as e:
                logger.error(f"查询节点信息失败: {e}")
                raise
    
    def save_layout(self, layout_data: List[Dict[str, Any]]) -> bool:
        """
        保存节点布局位置
        
        Args:
            layout_data: 布局数据列表
            
        Returns:
            是否成功
        """
        query = """
        MATCH (n)
        WHERE id(n) = $node_id
        SET n.layout_x = $x, n.layout_y = $y
        """
        with self.driver.session() as session:
            try:
                for item in layout_data:
                    session.run(
                        query,
                        node_id=int(item["node_id"]),
                        x=item["x"],
                        y=item["y"]
                    )
                return True
            
            except Exception as e:
                logger.error(f"保存布局失败: {e}")
                return False
    
    def create_paper_node(self, paper_data: Dict[str, Any]) -> str:
        """创建论文节点"""
        query = """
        CREATE (p:Paper $properties)
        RETURN id(p) as node_id
        """
        with self.driver.session() as session:
            result = session.run(query, properties=paper_data)
            record = result.single()
            return str(record["node_id"]) if record else None
    
    def create_author_node(self, author_data: Dict[str, Any]) -> str:
        """创建作者节点"""
        query = """
        CREATE (a:Author $properties)
        RETURN id(a) as node_id
        """
        with self.driver.session() as session:
            result = session.run(query, properties=author_data)
            record = result.single()
            return str(record["node_id"]) if record else None
    
    def create_organization_node(self, org_data: Dict[str, Any]) -> str:
        """创建单位节点"""
        query = """
        CREATE (o:Organization $properties)
        RETURN id(o) as node_id
        """
        with self.driver.session() as session:
            result = session.run(query, properties=org_data)
            record = result.single()
            return str(record["node_id"]) if record else None
    
    def create_relationship(self, start_id: str, end_id: str, rel_type: str, properties: Dict = None) -> bool:
        """创建关系"""
        query = f"""
        MATCH (a), (b)
        WHERE id(a) = $start_id AND id(b) = $end_id
        CREATE (a)-[r:{rel_type} $properties]->(b)
        RETURN r
        """
        with self.driver.session() as session:
            try:
                session.run(
                    query,
                    start_id=int(start_id),
                    end_id=int(end_id),
                    properties=properties or {}
                )
                return True
            except Exception as e:
                logger.error(f"创建关系失败: {e}")
                return False

