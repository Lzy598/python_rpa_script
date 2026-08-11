"""
数据库操作工具
影刀用法：配置数据库连接参数，直接执行SQL
"""

import pymysql
from pymysql.cursors import DictCursor
import json


class DatabaseManager:
    """数据库管理器"""
    
    def __init__(self, host, port, user, password, database):
        self.config = {
            'host': host,
            'port': int(port),
            'user': user,
            'password': password,
            'database': database,
            'charset': 'utf8mb4',
            'cursorclass': DictCursor
        }
        self.conn = None
    
    def connect(self):
        """建立连接"""
        if self.conn is None or not self.conn.open:
            self.conn = pymysql.connect(**self.config)
        return self.conn
    
    def close(self):
        """关闭连接"""
        if self.conn and self.conn.open:
            self.conn.close()
            self.conn = None
    
    def query(self, sql, params=None):
        """查询数据"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            return cursor.fetchall()
        finally:
            cursor.close()
    
    def query_one(self, sql, params=None):
        """查询单条"""
        rows = self.query(sql, params)
        return rows[0] if rows else None
    
    def execute(self, sql, params=None):
        """增删改"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            affected = cursor.execute(sql, params)
            conn.commit()
            return affected
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def execute_many(self, sql, params_list):
        """批量执行"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            affected = cursor.executemany(sql, params_list)
            conn.commit()
            return affected
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def insert_and_get_id(self, sql, params=None):
        """插入并返回自增ID"""
        conn = self.connect()
        cursor = conn.cursor()
        try:
            cursor.execute(sql, params)
            conn.commit()
            return cursor.lastrowid
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def sync_data_to_db(db_config, table_name, data_list, batch_size=500):
    """
    批量写入数据到数据库
    db_config: {host, port, user, password, database}
    data_list: [{'col1': val1, 'col2': val2}, ...]
    """
    if not data_list:
        return {'status': 'error', 'message': '无数据'}
    
    cols = list(data_list[0].keys())
    placeholders = ','.join(['%s'] * len(cols))
    columns = ','.join(cols)
    sql = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    
    db = DatabaseManager(**db_config)
    try:
        total = 0
        for i in range(0, len(data_list), batch_size):
            batch = data_list[i:i+batch_size]
            params = [[row[col] for col in cols] for row in batch]
            affected = db.execute_many(sql, params)
            total += affected
        
        return {
            'status': 'success',
            'total_rows': total,
            'batch_count': (total + batch_size - 1) // batch_size
        }
    finally:
        db.close()


# ===== 影刀入口 =====
if __name__ == '__main__':
    # 影刀传入参数
    db_host = "{{数据库地址}}"
    db_port = "{{端口}}"
    db_user = "{{用户名}}"
    db_pass = "{{密码}}"
    db_name = "{{数据库名}}"
    query_sql = "{{SQL语句}}"
    
    db = DatabaseManager(db_host, db_port, db_user, db_pass, db_name)
    try:
        rows = db.query(query_sql)
        # 输出到影刀：query_result
        query_result = rows
    finally:
        db.close()
