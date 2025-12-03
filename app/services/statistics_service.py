"""统计业务逻辑"""
from typing import List, Dict, Any
from app.repositories.mysql_dao import StatisticsDAO
from redis import Redis
import json
from loguru import logger
import hashlib

class StatisticsService:
    def __init__(self, dao: StatisticsDAO, cache: Redis = None):
        self.dao = dao
        self.cache = cache
    
    def query_statistics(self, query_params: Dict[str, Any]) -> Dict[str, Any]:
        cache_key = self._generate_cache_key(query_params)
        
        if self.cache:
            try:
                cached = self.cache.get(cache_key)
                if cached:
                    logger.info("从缓存获取统计数据")
                    return json.loads(cached)
            except Exception as e:
                logger.warning(f"缓存读取失败: {e}")
        
        try:
            data = self.dao.query_aggregated(query_params)
            
            result = {
                "metric": query_params.get("metric", ""),
                "data": data,
                "total": len(data)
            }
            
            if self.cache:
                try:
                    self.cache.setex(cache_key, 3600, json.dumps(result))
                except Exception as e:
                    logger.warning(f"缓存写入失败: {e}")
            
            return result
        
        except Exception as e:
            logger.error(f"查询统计数据失败: {e}")
            raise
    
    def _generate_cache_key(self, query_params: Dict[str, Any]) -> str:
        key_str = json.dumps(query_params, sort_keys=True)
        key_hash = hashlib.md5(key_str.encode()).hexdigest()
        return f"stat:{key_hash}"
    
    def clear_cache(self, metric: str = None):
        if not self.cache:
            return
        
        try:
            if metric:
                pattern = f"stat:*{metric}*"
            else:
                pattern = "stat:*"
            
            keys = self.cache.keys(pattern)
            if keys:
                self.cache.delete(*keys)
                logger.info(f"清除了 {len(keys)} 个缓存项")
        except Exception as e:
            logger.warning(f"清除缓存失败: {e}")

