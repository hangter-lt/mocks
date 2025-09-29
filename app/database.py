import sqlite3
import json
import os
import time
from datetime import datetime

# 数据库文件路径
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../requests.db')

def init_db():
    """初始化数据库，创建表"""
    conn = None
    try:
        # 使用连接池获取连接
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        # 创建请求日志表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                request_id TEXT UNIQUE,
                method TEXT,
                url TEXT,
                client_ip TEXT,
                request_headers TEXT,
                request_args TEXT,
                request_form TEXT,
                request_json TEXT,
                status_code INTEGER,
                response_headers TEXT,
                response_data TEXT,
                process_time REAL,
                timestamp TEXT,
                module TEXT
            )
        ''')
        
        conn.commit()
        # 关闭cursor
        cursor.close()
    except Exception as e:
        print(f"初始化数据库时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        # 释放连接回连接池
        release_db_connection(conn, pool)

def save_request_log(log_data):
    """保存请求日志到数据库"""
    conn = None
    try:
        # 使用连接池获取连接
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO request_logs (
                request_id, method, url, client_ip, request_headers, request_args, 
                request_form, request_json, status_code, response_headers, 
                response_data, process_time, timestamp, module
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            log_data['request_id'],
            log_data['method'],
            log_data['url'],
            log_data.get('client_ip', None),
            json.dumps(log_data['request_headers'], ensure_ascii=False),
            json.dumps(log_data['request_args'], ensure_ascii=False),
            json.dumps(log_data['request_form'], ensure_ascii=False),
            json.dumps(log_data['request_json'], ensure_ascii=False) if log_data['request_json'] else None,
            log_data['status_code'],
            json.dumps(log_data['response_headers'], ensure_ascii=False),
            json.dumps(log_data['response_data'], ensure_ascii=False) if log_data['response_data'] else None,
            log_data['process_time'],
            log_data['timestamp'],
            log_data.get('module', None)
        ))
        
        conn.commit()
        # 关闭cursor
        cursor.close()
    except Exception as e:
        print(f"保存请求日志时出错: {e}")
        if conn:
            conn.rollback()
    finally:
        # 释放连接回连接池
        release_db_connection(conn, pool)

# 创建数据库连接池
import sqlite3
import threading

# 数据库连接池类
class DatabaseConnectionPool:
    def __init__(self, db_path, max_connections=5):
        self.db_path = db_path
        self.max_connections = max_connections
        self.connections = []
        self.lock = threading.RLock()
        
    def get_connection(self):
        with self.lock:
            if len(self.connections) > 0:
                return self.connections.pop()
            # 创建新连接，在锁的保护下
            # 添加check_same_thread=False参数，允许在不同线程中使用连接
            conn = sqlite3.connect(self.db_path, check_same_thread=False)
            # 启用外键约束
            conn.execute('PRAGMA foreign_keys = ON')
            # 启用内存缓存
            conn.execute('PRAGMA cache_size = -64000')  # 约64MB缓存
            return conn
    
    def release_connection(self, conn):
        if conn:
            with self.lock:
                if len(self.connections) < self.max_connections:
                    try:
                        # 重置连接状态
                        conn.rollback()
                        self.connections.append(conn)
                    except Exception:
                        try:
                            conn.close()
                        except Exception:
                            pass
                else:
                    try:
                        conn.close()
                    except Exception:
                        pass

# 全局连接池实例
pool = DatabaseConnectionPool(DB_PATH, max_connections=10)

# 获取数据库连接
def get_db_connection():
    return pool.get_connection(), pool

# 释放数据库连接
def release_db_connection(conn, pool):
    if pool:
        pool.release_connection(conn)
    elif conn:
        try:
            conn.close()
        except Exception:
            pass

def get_requests_count(start_time=None, end_time=None, modules=None, status_code=None):
    """获取符合条件的请求日志总数"""
    conn = None
    try:
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询语句和参数
        query = 'SELECT COUNT(*) FROM request_logs WHERE 1=1'
        params = []
        
        # 添加时间范围筛选
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)
        
        # 添加模块筛选
        if modules:
            if isinstance(modules, list):
                # 处理多个模块参数
                if len(modules) > 0:
                    placeholders = ', '.join(['?' for _ in modules])
                    query += f' AND module IN ({placeholders})'
                    params.extend(modules)
            elif modules:  # 兼容单个模块参数
                query += ' AND module LIKE ?'
                params.append(f'%{modules}%')
        
        # 添加响应码筛选
        if status_code:
            query += ' AND status_code = ?'
            params.append(status_code)
        
        cursor.execute(query, params)
        count = cursor.fetchone()[0]
        
        # 关闭cursor
        cursor.close()
        return count
    except Exception as e:
        print(f"获取请求日志总数时出错: {e}")
        return 0
    finally:
        # 释放连接
        release_db_connection(conn, pool)
        

def get_all_requests(pagesize=None, current=None, start_time=None, end_time=None, modules=None, status_code=None):
    """获取请求日志，可以根据条件筛选"""
    conn = None
    try:
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        # 构建查询语句和参数
        query = 'SELECT * FROM request_logs WHERE 1=1'
        params = []
        
        # 添加时间范围筛选
        if start_time:
            query += ' AND timestamp >= ?'
            params.append(start_time)
        if end_time:
            query += ' AND timestamp <= ?'
            params.append(end_time)
        
        # 添加模块筛选
        if modules:
            if isinstance(modules, list):
                # 处理多个模块参数
                if len(modules) > 0:
                    placeholders = ', '.join(['?' for _ in modules])
                    query += f' AND module IN ({placeholders})'
                    params.extend(modules)
            elif modules:  # 兼容单个模块参数
                query += ' AND module LIKE ?'
                params.append(f'%{modules}%')
        
        # 添加响应码筛选
        if status_code:
            query += ' AND status_code = ?'
            params.append(status_code)
        
        # 添加排序
        query += ' ORDER BY id DESC'
        
        # 添加分页
        if pagesize and current:
            offset = (current - 1) * pagesize
            query += ' LIMIT ? OFFSET ?'
            params.extend([pagesize, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        # 获取列名
        column_names = [description[0] for description in cursor.description]
        
        # 将结果转换为字典列表
        results = []
        for row in rows:
            row_dict = dict(zip(column_names, row))
            # 对于列表查询，我们可以保持JSON字符串形式，减少解析开销
            # 只在详情页需要时才解析完整的JSON数据
            
            # 只解析必要的字段
            try:
                # 这些字段在列表展示中可能会用到
                row_dict['request_headers'] = json.loads(row_dict['request_headers']) if row_dict['request_headers'] else {}
                row_dict['response_headers'] = json.loads(row_dict['response_headers']) if row_dict['response_headers'] else {}
            except Exception as e:
                print(f"解析 JSON 数据时出错: {e}")
            
            # 其他字段保持原样，减少不必要的解析
            results.append(row_dict)
        
        # 关闭cursor
        cursor.close()
        return results
    except Exception as e:
        print(f"获取请求日志时出错: {e}")
        return []
    finally:
        # 释放连接
        release_db_connection(conn, pool)
        

def get_request_by_id(request_id):
    """根据请求ID获取特定请求日志"""
    conn = None
    try:
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        # 执行查询
        cursor.execute('SELECT * FROM request_logs WHERE request_id = ?', (request_id,))
        row = cursor.fetchone()
        
        # 如果没有找到记录，直接返回None
        if row is None:
            cursor.close()
            return None
        
        # 获取列名
        column_names = [description[0] for description in cursor.description]
        row_dict = dict(zip(column_names, row))
        
        # 解析所有JSON字段
        try:
            # 对于详情页，我们需要完整解析所有字段
            row_dict['request_headers'] = json.loads(row_dict['request_headers']) if row_dict['request_headers'] else {}
            row_dict['request_args'] = json.loads(row_dict['request_args']) if row_dict['request_args'] else {}
            row_dict['request_form'] = json.loads(row_dict['request_form']) if row_dict['request_form'] else {}
            row_dict['request_json'] = json.loads(row_dict['request_json']) if row_dict['request_json'] else None
            row_dict['response_headers'] = json.loads(row_dict['response_headers']) if row_dict['response_headers'] else {}
            row_dict['response_data'] = json.loads(row_dict['response_data']) if row_dict['response_data'] else None
        except Exception as e:
            print(f"解析 JSON 数据时出错: {e}")
        
        # 关闭cursor
        cursor.close()
        return row_dict
    except Exception as e:
        print(f"获取请求详情时出错: {e}")
        return None
    finally:
        # 释放连接
        release_db_connection(conn, pool)
        

def get_all_modules():
    """获取所有可用的模块列表"""
    conn = None
    try:
        conn, pool = get_db_connection()
        cursor = conn.cursor()
        
        # 查询所有不重复的模块名称，排除NULL值
        cursor.execute('SELECT DISTINCT module FROM request_logs WHERE module IS NOT NULL AND module != ""')
        rows = cursor.fetchall()
        
        # 提取模块名称
        modules = [row[0] for row in rows]
        
        # 关闭cursor
        cursor.close()
        return modules
    except Exception as e:
        print(f"获取模块列表时出错: {e}")
        return []
    finally:
        # 释放连接
        release_db_connection(conn, pool)