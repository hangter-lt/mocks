from flask import Blueprint, request, jsonify, render_template_string, send_from_directory
from ..database import get_all_requests, get_request_by_id, get_requests_count, get_all_modules
import os

bp = Blueprint('base', __name__)

# HTML模板
PAGE_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>请求日志列表</title>
    <link rel="icon" href="/favicon.ico" type="image/x-icon">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/layui@2.11.6/dist/css/layui.min.css">
    <script src="https://cdn.jsdelivr.net/npm/layui@2.11.6/dist/layui.min.js"></script>
    <style>
        body {
            background-color: #f5f5f5;
            margin: 0;
            padding: 0;
        }
        .container {
            width: 100%;
            height: 100vh;
            background-color: white;
            padding: 20px;
            box-sizing: border-box;
        }
        .method {
            font-weight: bold;
        }
        .GET {
            color: #009688;
        }
        .POST {
            color: #1E9FFF;
        }
        .PUT {
            color: #FFB800;
        }
        .DELETE {
            color: #FF5722;
        }
        .status-code {
            font-weight: bold;
        }
        .status-2xx {
            color: #009688;
        }
        .status-4xx {
            color: #FFB800;
        }
        .status-5xx {
            color: #FF5722;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        .header h1 {
            margin: 0;
        }
        .stats {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 4px;
            margin-bottom: 20px;
        }
        /* 流式加载样式 */
        .log-list {
            list-style: none;
            padding: 0;
            margin: 0;
        }
        
        .log-item {
            padding: 12px;
            border: 1px solid #e6e6e6;
            border-radius: 4px;
            margin-bottom: 8px;
            background-color: #fff;
            cursor: pointer;
            transition: all 0.3s;
            display: flex;
            flex-direction: column;
        }
        
        .log-item:hover {
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        .log-item.active {
            border-color: #1E9FFF;
            box-shadow: 0 2px 8px rgba(30, 159, 255, 0.2);
        }
        
        .log-item-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 6px;
        }
        
        .log-item-method {
            font-weight: bold;
            min-width: 60px;
            display: inline-block;
        }
        
        .log-item-status {
            font-weight: bold;
            min-width: 50px;
            display: inline-block;
        }
        
        .log-item-module {
            background-color: #17a2b8;
            color: white;
            padding: 2px 8px;
            border-radius: 3px;
            font-size: 12px;
            margin-left: 5px;
        }
        
        .log-item-url {
            word-break: break-all;
            color: #333;
            margin: 5px 0;
            font-size: 13px;
            line-height: 1.4;
            flex-grow: 1;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
        }
        
        .log-item-url:hover {
            -webkit-line-clamp: unset;
        }
        
        .log-item-bottom {
            display: flex;
            justify-content: space-between;
            font-size: 12px;
            color: #666;
            margin-top: 5px;
        }
        
        .log-item-time {
            font-size: 12px;
            color: #999;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #999;
        }
        
        .loading.hidden {
            display: none;
        }
        
        .no-more {
            text-align: center;
            padding: 20px;
            color: #999;
        }
        
        .no-more.hidden {
            display: none;
        }
        
        /* 新数据提醒样式 */
        .new-data-tip {
            background-color: #fff3cd;
            border: 1px solid #ffeaa7;
            border-radius: 4px;
            padding: 10px;
            margin-bottom: 10px;
            text-align: center;
            position: sticky;
            top: 0;
            z-index: 100;
        }
        
        .new-data-tip a {
            color: #007bff;
            text-decoration: none;
            font-weight: bold;
        }
        
        .new-data-tip a:hover {
            text-decoration: underline;
        }
        
        .detail-content {
            white-space: pre-wrap;
            word-break: break-all;
            font-family: monospace;
            background-color: #f8f9fa;
            padding: 10px;
            border-radius: 4px;
            /* 移除最大高度限制，让内容自由扩展 */
            overflow-y: auto;
            cursor: pointer;
            position: relative;
        }
        
        .detail-content:hover {
            background-color: #e9ecef;
        }
        
        .copy-tooltip {
            position: absolute;
            top: 5px;
            right: 5px;
            background-color: #495057;
            color: white;
            padding: 2px 6px;
            border-radius: 3px;
            font-size: 10px;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        
        .detail-content:hover .copy-tooltip {
            opacity: 1;
        }
        .layout-container {
            display: flex;
            gap: 20px;
            height: calc(100vh - 120px);
        }
        .list-panel {
            flex: 0 0 300px;
            overflow: auto;
        }
        .detail-panel {
            flex: 1;
            border-left: 1px solid #eee;
            padding-left: 20px;
            overflow: auto;
        }
        .detail-placeholder {
            text-align: center;
            color: #999;
            padding: 50px 20px;
        }
        .detail-section {
            margin-bottom: 30px;
        }
        .detail-section h3 {
            border-bottom: 1px solid #eee;
            padding-bottom: 5px;
            margin-bottom: 15px;
        }
        .hidden {
            display: none;
        }
        .detail-layout {
            display: flex;
            gap: 20px;
            height: calc(100vh - 160px);
        }
        .detail-left {
            flex: 1;
            overflow: auto;
        }
        .detail-right {
            flex: 1;
            overflow: auto;
            border-left: 1px solid #eee;
            padding-left: 20px;
        }
        
        /* 固定筛选表单和统计信息不随滚动条滚动 */
        /* 使用容器来包裹两个元素，确保它们完全贴合 */
        /* 确保父容器不会影响粘性定位 */
        .list-panel {
            position: relative;
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
            box-sizing: border-box;
        }
        
        /* 固定头部容器 - 增强粘性定位效果 */
        .fixed-header-container {
            position: sticky;
            top: 0;
            z-index: 100;
            background-color: #fff;
            display: flex;
            flex-direction: column;
            width: 100%;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.3s ease;
        }
        
        /* 内容容器 */
        .content-container {
            flex: 1;
            width: 100%;
            overflow-y: auto;
            padding: 10px 0;
            transition: all 0.3s ease;
            box-sizing: border-box;
        }
        
        /* 统计信息区域 */
        .stats {
            padding: 10px 0;
            margin: 0;
            box-shadow: 0 1px 0 rgba(0,0,0,0.05);
            height: 40px;
            box-sizing: border-box;
            background-color: #fff;
        }
        
        /* 筛选表单区域 */
        .filter-form {
            margin: 0 !important;
            background-color: #f8f9fa;
            box-sizing: border-box;
            border-top: 1px solid #eee;
            overflow: hidden;
        }
        
        /* 筛选表单头部 - 用于折叠按钮 */
        .filter-header {
            padding: 10px 15px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            cursor: pointer;
        }
        
        /* 筛选表单内容 */
        .filter-content {
            padding: 0 15px 15px;
            max-height: 500px;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        
        /* 折叠状态下的表单内容 */
        .filter-form.collapsed .filter-content {
            max-height: 0;
            padding-bottom: 0;
        }
        
        /* 折叠图标 */
        .collapse-icon {
            transition: transform 0.3s ease;
        }
        
        /* 折叠状态下的图标 */
        .filter-form.collapsed .collapse-icon {
            transform: rotate(-90deg);
        }
        
        /* 新数据提示样式 */
        #new-data-tip {
            padding: 8px 12px;
            background-color: #f0f9ff;
            border: 1px solid #bae7ff;
            border-radius: 4px;
            text-align: center;
        }
        
        /* 日志列表样式 */
        .log-list {
            padding: 0 0px;
        }
        
        /* 加载状态样式 */
        .loading,
        .no-more {
            text-align: center;
            padding: 20px 0;
            color: #999;
        }

        /* 标签风格 */
        .layui-form-radio>.lay-skin-tag,
        .layui-form-checkbox>.lay-skin-tag {
            font-size: 13px;
            border-radius: 100px;
        }
        .layui-form-checked>.lay-skin-tag,
        .layui-form-radioed>.lay-skin-tag {
            color: #fff !important;
            background-color: #16b777 !important;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>请求日志列表</h1>
        </div>
        
        <div class="layout-container">
            <!-- 左侧列表 -->
            <div class="list-panel">
                <div class="fixed-header-container">
                    <div class="stats">
                        <span>总计: <span id="total-count">0</span> 条记录</span>
                        <span style="float: right;">
                            <input type="checkbox" id="auto-refresh" checked/>
                            <label for="auto-refresh">自动刷新</label>
                        </span>
                    </div>
                    
                    <!-- 筛选表单 -->
                    <div class="filter-form layui-form">
                        <div class="filter-header">
                            <span>筛选条件</span>
                            <i class="layui-icon collapse-icon layui-icon-down"></i>
                        </div>
                        <div class="filter-content">
                            <div style="margin-bottom: 10px;">
                                <label class="layui-form-label">开始时间:</label>
                                <div class="layui-input-block">
                                    <input type="text" id="start-time" class="layui-input" placeholder="选择开始时间" autocomplete="off" />
                                </div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label class="layui-form-label">结束时间:</label>
                                <div class="layui-input-block">
                                    <input type="text" id="end-time" class="layui-input" placeholder="选择结束时间" autocomplete="off" />
                                </div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label class="layui-form-label">模块:</label>
                                <div class="layui-input-block" id="module-container">
                                    <div id="module" class="layui-form">
                                        <!-- 模块checkbox将通过JavaScript动态加载 -->
                                    </div>
                                </div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <label class="layui-form-label">响应码:</label>
                                <div class="layui-input-block">
                                    <input type="number" id="status-code" class="layui-input" placeholder="输入响应码" min="100" max="599" />
                                </div>
                            </div>
                            <div style="margin-top: 10px; display: flex; gap: 10px;">
                                <button id="reset-btn" class="layui-btn layui-btn-primary" style="flex: 1;">重置</button>
                                <button id="search-btn" class="layui-btn layui-btn-blue" style="flex: 1;">搜索</button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <div class="content-container">
                <div id="new-data-tip" class="new-data-tip hidden">
                    <span>有新的数据，请<a href="#" id="load-new-data">点击刷新</a></span>
                </div>
                
                <ul class="log-list" id="log-list">
                    <!-- 日志列表将通过 AJAX 加载 -->
                </ul>
                
                <div class="loading hidden" id="loading">
                    <i class="layui-icon layui-icon-loading layui-icon layui-anim layui-anim-rotate layui-anim-loop"></i>
                    加载中...
                </div>
                
                <div class="no-more hidden" id="no-more">
                    没有更多数据了
                </div>
                </div>
            </div>
            
            <!-- 右侧详情 -->
            <div class="detail-panel">
                <div id="detail-content">
                    <div class="detail-placeholder">
                        <i class="layui-icon layui-icon-tabs" style="font-size: 36px;"></i>
                        <p>点击左侧列表中的任意一项查看详细信息</p>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // 全局变量
        var page = 1;
        var pageSize = 20;
        var total = 0;
        var isLoading = false;
        var hasMore = true;
        var contentContainer = document.querySelector('.content-container');
        var latestLogId = null;
        var autoRefreshInterval = null;
        var isAutoRefresh = false;
        var currentFilters = {};
        
        layui.use(['layer', 'laydate', 'form'], function(){
            var layer = layui.layer;
            var laydate = layui.laydate;
            var form = layui.form;
            
            // 初始化表单
            form.render();
            
            // 初始化模块选择下拉框
            moduleSelect = layui.form;
            
            // 加载模块列表
            loadModules();
            
            // 设置开始时间默认一小时前
            var now = new Date();
            var oneHourAgo = new Date(now.getTime() - 60 * 60 * 1000);
            
            // 格式化日期时间（yyyy-MM-dd HH:mm:ss）
            function formatDateTime(date) {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');
                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            }
            
            // 设置默认值
            document.getElementById('start-time').value = formatDateTime(oneHourAgo);
            
            // 初始化日期时间选择器
            laydate.render({
                elem: '#start-time',
                type: 'datetime',
                format: 'yyyy-MM-dd HH:mm:ss',
                fullPanel: true
            });
            
            laydate.render({
                elem: '#end-time',
                type: 'datetime',
                format: 'yyyy-MM-dd HH:mm:ss',
                fullPanel: true
            });
            
            // 页面加载完成后获取第一页数据
                // 初始化当前筛选条件
                currentFilters = getCurrentFilters();
                
                loadLogs();
                
                // 监听滚动事件实现无限滚动
                contentContainer.addEventListener('scroll', function() {
                    console.log('滚动事件触发');
                    console.log('滚动位置: scrollTop=' + contentContainer.scrollTop + ', clientHeight=' + contentContainer.clientHeight + ', scrollHeight=' + contentContainer.scrollHeight);
                    // 如果正在加载或者没有更多数据，则不处理
                    if (isLoading || !hasMore) {
                        console.log('不加载更多: isLoading=' + isLoading + ', hasMore=' + hasMore);
                        return;
                    }
                    
                    // 计算是否滚动到底部
                    var scrollTop = contentContainer.scrollTop;
                    var clientHeight = contentContainer.clientHeight;
                    var scrollHeight = contentContainer.scrollHeight;
                    
                    // 当滚动到距离底部50px以内时加载更多
                    if (scrollTop + clientHeight >= scrollHeight - 50) {
                        console.log('触发加载更多数据，当前页: ' + page);
                        loadLogs();
                    }
                });
                    
                    // 初始化自动刷新状态
                    isAutoRefresh = document.getElementById('auto-refresh').checked;
                    if (isAutoRefresh) {
                        // 每5秒检查一次新数据
                        autoRefreshInterval = setInterval(checkNewData, 5000);
                    }
                    
                    // 自动刷新功能
                    document.getElementById('auto-refresh').addEventListener('change', function() {
                        isAutoRefresh = this.checked;
                        if (isAutoRefresh) {
                            // 每5秒检查一次新数据
                            autoRefreshInterval = setInterval(checkNewData, 5000);
                        } else {
                            clearInterval(autoRefreshInterval);
                        }
                    });
                    
                    // 筛选表单折叠功能
                    var filterForm = document.querySelector('.filter-form');
                    var filterHeader = document.querySelector('.filter-header');
                    
                    // 默认展开表单
                    filterForm.classList.remove('collapsed');
                    
                    // 点击头部切换折叠状态
                    filterHeader.addEventListener('click', function() {
                        filterForm.classList.toggle('collapsed');
                    });
                    
                    // 手动加载新数据
                    document.getElementById('load-new-data').addEventListener('click', function(e) {
                        e.preventDefault();
                        refreshNewData();
                    });
                    
                    // 搜索按钮点击事件
                    document.getElementById('search-btn').addEventListener('click', function() {
                        // 获取新的筛选条件
                        currentFilters = getCurrentFilters();
                        
                        // 重置分页状态
                        page = 1;
                        hasMore = true;
                        document.getElementById('log-list').innerHTML = '';
                        document.getElementById('no-more').classList.add('hidden');
                        
                        // 重新加载日志
                        loadLogs();
                    });
                    
                    // 重置按钮点击事件
                    document.getElementById('reset-btn').addEventListener('click', function() {
                        // 清除所有筛选输入框的值
                        document.getElementById('start-time').value = '';
                        document.getElementById('end-time').value = '';
                        document.getElementById('status-code').value = '';
                        
                        // 重置多选模块checkbox
                        document.querySelectorAll('input[name="modules"]').forEach(checkbox => {
                            checkbox.checked = false;
                        });
                        layui.form.render('checkbox');
                        
                        // 重置筛选条件
                        currentFilters = {};
                        
                        // 重置分页状态
                        page = 1;
                        hasMore = true;
                        document.getElementById('log-list').innerHTML = '';
                        document.getElementById('no-more').classList.add('hidden');
                        
                        // 重新加载日志
                        loadLogs();
                    });

            
            // 检查是否有新数据
            function checkNewData() {
                if (isLoading) return;
                
                // 构建查询参数，包含当前筛选条件
                var params = new URLSearchParams();
                params.append('page', 1);
                params.append('size', 1);
                
                // 添加当前筛选条件
                if (currentFilters.start_time) {
                    params.append('start_time', currentFilters.start_time);
                }
                if (currentFilters.end_time) {
                    params.append('end_time', currentFilters.end_time);
                }
                if (currentFilters.modules && currentFilters.modules.length > 0) {
                    // 对于多选的模块，每个模块都添加一个module参数
                    currentFilters.modules.forEach(module => {
                        params.append('module', module);
                    });
                }
                if (currentFilters.status_code) {
                    params.append('status_code', currentFilters.status_code);
                }
                
                fetch(`/.api/requests?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (data.errCode === 0 && data.data.logs.length > 0) {
                        var newestLog = data.data.logs[0];
                        if (latestLogId === null) {
                            latestLogId = newestLog.request_id;
                        } else if (newestLog.request_id !== latestLogId) {
                            // 有新数据
                            document.getElementById('new-data-tip').classList.remove('hidden');
                        }
                    }
                })
                .catch(error => {
                    console.error('检查新数据失败: ' + error.message);
                });
            }
            
            // 刷新新数据
            function refreshNewData() {
                // 重置状态
                page = 1;
                hasMore = true;
                latestLogId = null;
                document.getElementById('log-list').innerHTML = '';
                document.getElementById('new-data-tip').classList.add('hidden');
                document.getElementById('no-more').classList.add('hidden');
                loadLogs();
            }
            
            // 加载模块列表
            function loadModules() {
                fetch('/.api/modules')
                    .then(response => response.json())
                    .then(data => {
                        if (data.errCode === 0) {
                            var moduleContainer = document.getElementById('module');
                            // 清空现有选项
                            moduleContainer.innerHTML = '';
                            
                            // 添加checkbox选项
                            data.data.forEach(module => {
                                var checkboxHtml = `
                                    <input type="checkbox" name="modules" lay-skin="none" title="${module}" value="${module}">
                                    <div lay-checkbox class="lay-skin-tag layui-badge">${module}</div>
                                `;
                                moduleContainer.innerHTML += checkboxHtml;
                            });
                            
                            // 重新渲染checkbox组件
                            layui.form.render('checkbox');
                        } else {
                            layer.msg('加载模块列表失败: ' + data.errMsg);
                        }
                    })
                    .catch(error => {
                        console.error('加载模块列表失败: ' + error.message);
                        layer.msg('加载模块列表失败');
                    });
            }
            
            // 获取当前筛选条件
            function getCurrentFilters() {
                var start_time = document.getElementById('start-time').value;
                var end_time = document.getElementById('end-time').value;
                var status_code = document.getElementById('status-code').value;
                
                // 获取选中的模块（多选）
                var selectedModules = Array.from(document.querySelectorAll('input[name="modules"]:checked')).map(checkbox => checkbox.value);
                
                // 格式化日期时间（laydate返回的格式是 yyyy-MM-dd HH:mm:ss）
                if (start_time) {
                    // 将laydate格式的日期时间转换为时间戳
                    start_time = new Date(start_time.replace(/-/g, '/')).getTime() / 1000;
                }
                if (end_time) {
                    // 将laydate格式的日期时间转换为时间戳
                    end_time = new Date(end_time.replace(/-/g, '/')).getTime() / 1000;
                }
                
                return {
                    start_time: start_time,
                    end_time: end_time,
                    modules: selectedModules.length > 0 ? selectedModules : null,
                    status_code: status_code
                };
            }
            
            // 加载日志列表
            function loadLogs() {
                console.log('loadLogs被调用，当前页: ' + page + ', isLoading: ' + isLoading + ', hasMore: ' + hasMore);
                // 如果正在加载或者没有更多数据，则不处理
                if (isLoading || !hasMore) return;
                
                isLoading = true;
                document.getElementById('loading').classList.remove('hidden');
                
                // 构建查询参数
                var params = new URLSearchParams();
                params.append('page', page);
                params.append('size', pageSize);
                
                // 添加筛选条件
                if (currentFilters.start_time) {
                    params.append('start_time', currentFilters.start_time);
                }
                if (currentFilters.end_time) {
                    params.append('end_time', currentFilters.end_time);
                }
                if (currentFilters.modules && currentFilters.modules.length > 0) {
                    // 对于多选的模块，每个模块都添加一个module参数
                    currentFilters.modules.forEach(module => {
                        params.append('module', module);
                    });
                }
                if (currentFilters.status_code) {
                    params.append('status_code', currentFilters.status_code);
                }
                
                fetch(`/.api/requests?${params.toString()}`)
                .then(response => response.json())
                .then(data => {
                    if (data.errCode === 0) {
                        // 更新统计信息
                        total = data.data.total;
                        document.getElementById('total-count').textContent = total;
                        
                        // 更新最新日志ID
                        if (data.data.logs.length > 0 && page === 1) {
                            latestLogId = data.data.logs[0].request_id;
                        }
                        
                        // 渲染日志列表
                        renderLogs(data.data.logs);
                        
                        // 更新分页信息
                        if (data.data.logs.length < pageSize) {
                            hasMore = false;
                            document.getElementById('no-more').classList.remove('hidden');
                        } else {
                            page++;
                        }
                    } else {
                        layer.msg('获取日志列表失败: ' + data.errMsg);
                        hasMore = false;
                    }
                    
                    isLoading = false;
                    document.getElementById('loading').classList.add('hidden');
                })
                .catch(error => {
                    layer.msg('获取日志列表失败: ' + error.message);
                    isLoading = false;
                    document.getElementById('loading').classList.add('hidden');
                    hasMore = false;
                });
            }
            
            // 格式化时间戳为本地时间
            function formatISOTime(timestamp) {
                if (!timestamp) return '';
                // 确保时间戳是数字类型
                const timestampNum = typeof timestamp === 'string' ? parseFloat(timestamp) : timestamp;
                const date = new Date(timestampNum * 1000); // 乘以1000转换为毫秒
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');
                const seconds = String(date.getSeconds()).padStart(2, '0');
                return `${year}-${month}-${day} ${hours}:${minutes}:${seconds}`;
            }
            
            // 渲染日志列表
            function renderLogs(logs) {
                var logList = document.getElementById('log-list');
                
                // 如果是第一页，则替换内容，否则追加到末尾
                if (page === 1) {
                    logList.innerHTML = '';
                }
                
                logs.forEach(log => {
                    var li = document.createElement('li');
                    li.className = 'log-item';
                    li.setAttribute('data-request-id', log.request_id);
                    li.innerHTML = `
                        <div class="log-item-header">
                            <span class="log-item-method method ${log.method}">${log.method}</span>
                            <span class="log-item-status status-code status-${log.status_code}${Math.floor(log.status_code/100)}xx">${log.status_code}</span>
                        </div>
                        <div class="log-item-url">${log.url}</div>
                        <div class="log-item-bottom">
                            <span class="log-item-time">${formatISOTime(log.timestamp)}</span>
                            ${log.module ? `<span class="log-item-module">${log.module}</span>` : ''}
                        </div>
                    `;
                    logList.appendChild(li);
                });
                
                // 为新添加的项绑定点击事件
                var logItems = document.querySelectorAll('.log-item:not([data-click-bound])');
                logItems.forEach(function(item) {
                    item.setAttribute('data-click-bound', 'true');
                    item.addEventListener('click', function() {
                        // 移除所有项的激活样式
                        document.querySelectorAll('.log-item').forEach(i => i.classList.remove('active'));
                        // 为当前项添加激活样式
                        this.classList.add('active');
                        
                        var requestId = this.getAttribute('data-request-id');
                        showRequestDetail(requestId);
                    });
                });
            }
            
            // 显示请求详情
            function showRequestDetail(requestId) {
                fetch('/.api/requests/' + requestId)
                .then(response => response.json())
                .then(data => {
                    if (data.errCode === 0) {
                        var log = data.data;
                        var detailContent = `
                            <div class="detail-layout">
                                <div class="detail-left">
                                    <div class="detail-section">
                                        <h3>基本信息</h3>
                                        <div><strong>请求方法:</strong> <span class="method ${log.method}">${log.method}</span></div>
                                        <div><strong>请求PATH:</strong> ${log.url}</div>
                                        <div><strong>请求时间:</strong> ${formatISOTime(log.timestamp)}</div>
                                        <div><strong>客户端IP:</strong> ${log.client_ip || '未知'}</div>
                                    </div>
                                    
                                    <div class="detail-section">
                                        <h3>请求信息</h3>
                                        <div><strong>请求头:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.request_headers, null, 2)}</div>
                                        <div><strong>请求参数:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.request_args, null, 2)}</div>
                                        <div><strong>表单数据:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.request_form, null, 2)}</div>
                                        <div><strong>JSON数据:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.request_json, null, 2)}</div>
                                    </div>
                                </div>
                                <div class="detail-right">
                                    <div class="detail-section">
                                        <h3>响应信息</h3>
                                        <div><strong>状态码:</strong> <span class="status-code status-${log.status_code}${Math.floor(log.status_code/100)}xx">${log.status_code}</span></div>
                                        <div><strong>响应头:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.response_headers, null, 2)}</div>
                                        <div><strong>响应数据:</strong></div>
                                        <div class="detail-content">${JSON.stringify(log.response_data, null, 2)}</div>
                                    </div>
                                </div>
                            </div>
                        `;
                        
                        document.getElementById('detail-content').innerHTML = detailContent;
                        
                        // 添加一键复制功能
                        addCopyFunctionality();
                    } else {
                        document.getElementById('detail-content').innerHTML = `
                            <div class="detail-placeholder">
                                <p>获取详情失败: ${data.errMsg}</p>
                            </div>
                        `;
                    }
                })
                .catch(error => {
                    document.getElementById('detail-content').innerHTML = `
                        <div class="detail-placeholder">
                            <p>获取详情失败: ${error.message}</p>
                        </div>
                    `;
                });
            }
        // 一键复制功能
        function addCopyFunctionality() {
            var contentDivs = document.querySelectorAll('.detail-content');
            contentDivs.forEach(function(div) {
                // 检查是否已经添加过复制功能
                if (div.hasAttribute('data-copy-added')) {
                    return;
                }
                
                // 添加复制提示
                var tooltip = document.createElement('div');
                tooltip.className = 'copy-tooltip';
                tooltip.textContent = '点击复制';
                div.appendChild(tooltip);
                
                // 绑定点击事件
                div.addEventListener('click', function() {
                    // 获取div内容
                    var content = this.textContent.replace('点击复制', '').trim();
                    
                    // 创建临时textarea元素
                    var textarea = document.createElement('textarea');
                    textarea.value = content;
                    textarea.style.position = 'fixed';
                    textarea.style.left = '-999999px';
                    textarea.style.top = '-999999px';
                    document.body.appendChild(textarea);
                    
                    // 选择并复制文本
                    textarea.focus();
                    textarea.select();
                    
                    try {
                        // 执行复制命令
                        document.execCommand('copy');
                        
                        // 显示复制成功提示
                        var originalText = tooltip.textContent;
                        tooltip.textContent = '已复制！';
                        tooltip.style.backgroundColor = '#28a745';
                        
                        // 2秒后恢复原提示
                        setTimeout(function() {
                            tooltip.textContent = originalText;
                            tooltip.style.backgroundColor = '#495057';
                        }, 2000);
                    } catch (err) {
                        console.error('复制失败:', err);
                    } finally {
                        // 移除临时元素
                        document.body.removeChild(textarea);
                    }
                });
                
                // 标记已添加复制功能
                div.setAttribute('data-copy-added', 'true');
            });
        }
        
        });
    </script>
</body>
</html>
'''

LOGS_API_TEMPLATE = '''
{
    "errCode": 0,
    "errMsg": "Success",
    "data": {
        "logs": {{ logs | tojson }},
        "page": {{ page }},
        "size": {{ size }},
        "total": {{ total }},
        "total_pages": {{ total_pages }}
    }
}
'''

REQUEST_DETAIL_TEMPLATE = '''
{
    "errCode": 0,
    "errMsg": "Success",
    "data": {{ log | tojson }}
}
'''

@bp.route('/favicon.ico')
def favicon():
    """favicon图标接口"""
    # 返回用户提供的SVG图像
    svg_data = """<svg t="1757559104511" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="7718" width="256" height="256"><path d="M512 512m-414 0a414 414 0 1 0 828 0 414 414 0 1 0-828 0Z" fill="#F0C48A" p-id="7719"></path><path d="M248.138 274.23h348.34v442.146h-348.34z" fill="#FFFFFF" p-id="7720"></path><path d="M545.58 274.23h50.898v442.146H545.58z" fill="#D3E6F8" p-id="7721"></path><path d="M248.138 274.23h348.34v103.818h-348.34z" fill="#D3E6F8" p-id="7722"></path><path d="M545.58 274.23h50.898v103.818H545.58z" fill="#A4CFF2" p-id="7723"></path><path d="M596.48 725.55H248.14a9.172 9.172 0 0 1-9.172-9.172V274.23a9.172 9.172 0 0 1 9.172-9.172h348.34a9.172 9.172 0 0 1 9.172 9.172v442.146a9.174 9.174 0 0 1-9.172 9.174z m-339.168-18.346h329.994v-423.8H257.312v423.8z" fill="#4C4372" p-id="7724"></path><path d="M596.48 387.222H248.14a9.172 9.172 0 0 1-9.172-9.172v-103.818a9.172 9.172 0 0 1 9.172-9.172h348.34a9.172 9.172 0 0 1 9.172 9.172v103.818a9.172 9.172 0 0 1-9.172 9.172z m-339.168-18.346h329.994v-85.472H257.312v85.472zM545.58 458.542H299.04a9.172 9.172 0 1 1 0-18.344h246.54a9.172 9.172 0 0 1 0 18.344zM422.308 526.49H299.04a9.172 9.172 0 0 1 0-18.344h123.272a9.172 9.172 0 1 1-0.004 18.344zM422.308 594.438H299.04a9.172 9.172 0 0 1 0-18.344h123.272a9.172 9.172 0 1 1-0.004 18.344zM422.308 662.386H299.04a9.172 9.172 0 0 1 0-18.344h123.272a9.172 9.172 0 1 1-0.004 18.344z" fill="#4C4372" p-id="7725"></path><path d="M746.822 674.878v-53.602h-36.078a116.024 116.024 0 0 0-14.336-34.576l25.52-25.52-37.902-37.902-25.52 25.52a116.002 116.002 0 0 0-34.576-14.336v-36.078h-53.602v36.078a116.024 116.024 0 0 0-34.576 14.336l-25.52-25.52-37.902 37.902 25.52 25.52a116.002 116.002 0 0 0-14.336 34.576h-36.078v53.602h36.078a116.024 116.024 0 0 0 14.336 34.576l-25.52 25.52 37.902 37.902 25.52-25.52a116.002 116.002 0 0 0 34.576 14.336v36.078h53.602v-36.078a116.024 116.024 0 0 0 34.576-14.336l25.52 25.52 37.902-37.902-25.52-25.52a116.002 116.002 0 0 0 14.336-34.576h36.078z m-149.694 37.576c-35.554 0-64.376-28.822-64.376-64.376s28.822-64.376 64.376-64.376 64.376 28.822 64.376 64.376c0.002 35.554-28.822 64.376-64.376 64.376z" fill="#FD919E" p-id="7726"></path><path d="M815.86 448.01v-32.232h-21.694a69.78 69.78 0 0 0-8.62-20.79l15.346-15.346-22.792-22.792-15.346 15.346a69.728 69.728 0 0 0-20.79-8.62v-21.694h-32.232v21.694a69.78 69.78 0 0 0-20.79 8.62l-15.346-15.346-22.792 22.792 15.346 15.346a69.728 69.728 0 0 0-8.62 20.79h-21.694v32.232h21.694a69.78 69.78 0 0 0 8.62 20.79l-15.346 15.346 22.792 22.792 15.346-15.346a69.728 69.728 0 0 0 20.79 8.62v21.694h32.232v-21.694a69.78 69.78 0 0 0 20.79-8.62l15.346 15.346 22.792-22.792-15.346-15.346a69.728 69.728 0 0 0 8.62-20.79h21.694z m-90.01 22.596c-21.378 0-38.71-17.332-38.71-38.71s17.33-38.712 38.71-38.712c21.378 0 38.71 17.33 38.71 38.712 0 21.376-17.33 38.71-38.71 38.71z" fill="#E8677D" p-id="7727"></path><path d="M623.93 806.942h-53.602a9.172 9.172 0 0 1-9.172-9.172V768.74a124.814 124.814 0 0 1-23.902-9.912l-20.536 20.536a9.172 9.172 0 0 1-12.972 0l-37.902-37.902a9.172 9.172 0 0 1 0-12.972l20.536-20.536a124.76 124.76 0 0 1-9.912-23.902h-29.03a9.172 9.172 0 0 1-9.172-9.172v-53.602a9.172 9.172 0 0 1 9.172-9.172h29.03a124.942 124.942 0 0 1 9.912-23.902l-20.536-20.536a9.172 9.172 0 0 1 0-12.972l37.902-37.902a9.17 9.17 0 0 1 12.972 0l20.536 20.536a124.89 124.89 0 0 1 23.902-9.912v-29.03a9.172 9.172 0 0 1 9.172-9.172h53.602a9.172 9.172 0 0 1 9.172 9.172v29.03a124.814 124.814 0 0 1 23.902 9.912l20.536-20.536a9.172 9.172 0 0 1 12.972 0l37.902 37.902a9.17 9.17 0 0 1 0 12.972l-20.536 20.536a124.814 124.814 0 0 1 9.912 23.902h29.03a9.172 9.172 0 0 1 9.172 9.172v53.602a9.172 9.172 0 0 1-9.172 9.172h-29.03a125.014 125.014 0 0 1-9.912 23.904l20.536 20.536a9.17 9.17 0 0 1 0 12.972l-37.902 37.902a9.172 9.172 0 0 1-12.972 0l-20.536-20.536a124.76 124.76 0 0 1-23.902 9.912v29.03a9.172 9.172 0 0 1-9.172 9.17z m-44.428-18.346h35.256v-26.906a9.174 9.174 0 0 1 7.074-8.93 106.686 106.686 0 0 0 31.842-13.202 9.172 9.172 0 0 1 11.318 1.312l19.036 19.034 24.93-24.93-19.036-19.034a9.176 9.176 0 0 1-1.312-11.318 106.69 106.69 0 0 0 13.204-31.842 9.176 9.176 0 0 1 8.93-7.076h26.906v-35.256h-26.906a9.174 9.174 0 0 1-8.93-7.076 106.686 106.686 0 0 0-13.202-31.842 9.176 9.176 0 0 1 1.31-11.318l19.036-19.034-24.93-24.93-19.036 19.034a9.176 9.176 0 0 1-11.318 1.312 106.634 106.634 0 0 0-31.842-13.202 9.174 9.174 0 0 1-7.074-8.93v-26.906h-35.256v26.906a9.174 9.174 0 0 1-7.074 8.93 106.728 106.728 0 0 0-31.844 13.202 9.174 9.174 0 0 1-11.318-1.312l-19.034-19.034-24.93 24.93 19.034 19.034a9.176 9.176 0 0 1 1.312 11.318 106.68 106.68 0 0 0-13.204 31.844 9.174 9.174 0 0 1-8.93 7.074h-26.906v35.256h26.906a9.174 9.174 0 0 1 8.93 7.074 106.732 106.732 0 0 0 13.204 31.844 9.176 9.176 0 0 1-1.312 11.318l-19.034 19.034 24.93 24.93 19.034-19.034a9.176 9.176 0 0 1 11.318-1.312 106.624 106.624 0 0 0 31.844 13.202 9.174 9.174 0 0 1 7.074 8.93v26.906z m17.626-66.968c-40.554 0-73.55-32.994-73.55-73.55s32.994-73.55 73.55-73.55 73.55 32.994 73.55 73.55-32.992 73.55-73.55 73.55z m0-128.756c-30.44 0-55.204 24.764-55.204 55.204s24.764 55.204 55.204 55.204 55.204-24.764 55.204-55.204-24.764-55.204-55.204-55.204z" fill="#4C4372" p-id="7728"></path><path d="M741.966 531.078h-32.232a9.172 9.172 0 0 1-9.172-9.172v-14.78a78.472 78.472 0 0 1-10.022-4.156l-10.452 10.454a9.17 9.17 0 0 1-12.972 0l-22.792-22.792a9.17 9.17 0 0 1 0-12.972l10.452-10.454a78.498 78.498 0 0 1-4.156-10.024h-14.78a9.172 9.172 0 0 1-9.172-9.172v-32.232a9.172 9.172 0 0 1 9.172-9.172h14.78a78.618 78.618 0 0 1 4.156-10.024l-10.452-10.454a9.17 9.17 0 0 1 0-12.972l22.792-22.79a9.172 9.172 0 0 1 12.972 0l10.452 10.454a78.712 78.712 0 0 1 10.022-4.156v-14.78a9.172 9.172 0 0 1 9.172-9.172h32.232a9.172 9.172 0 0 1 9.172 9.172v14.78a78.618 78.618 0 0 1 10.024 4.156l10.452-10.454a9.172 9.172 0 0 1 12.972 0l22.792 22.79a9.17 9.17 0 0 1 0 12.972l-10.454 10.454a78.712 78.712 0 0 1 4.156 10.022h14.778a9.172 9.172 0 0 1 9.172 9.172v32.232a9.172 9.172 0 0 1-9.172 9.172h-14.778a78.592 78.592 0 0 1-4.156 10.022l10.454 10.454a9.17 9.17 0 0 1 0 12.972l-22.792 22.792a9.174 9.174 0 0 1-12.972 0l-10.452-10.454a78.618 78.618 0 0 1-10.024 4.156v14.78a9.174 9.174 0 0 1-9.172 9.176z m-23.06-18.346h13.886v-12.52a9.174 9.174 0 0 1 7.074-8.93c6.384-1.5 12.46-4.02 18.058-7.488a9.172 9.172 0 0 1 11.318 1.312l8.86 8.86 9.818-9.818-8.86-8.86a9.174 9.174 0 0 1-1.312-11.316 60.558 60.558 0 0 0 7.488-18.058 9.176 9.176 0 0 1 8.93-7.076h12.52v-13.886h-12.52a9.174 9.174 0 0 1-8.93-7.076 60.558 60.558 0 0 0-7.488-18.058 9.172 9.172 0 0 1 1.312-11.316l8.86-8.86-9.818-9.818-8.86 8.86a9.174 9.174 0 0 1-11.316 1.312 60.514 60.514 0 0 0-18.058-7.488 9.174 9.174 0 0 1-7.074-8.93v-12.52h-13.886v12.52a9.174 9.174 0 0 1-7.074 8.93 60.534 60.534 0 0 0-18.056 7.488 9.174 9.174 0 0 1-11.318-1.312l-8.86-8.86-9.818 9.818 8.86 8.86a9.172 9.172 0 0 1 1.31 11.318 60.476 60.476 0 0 0-7.486 18.056 9.176 9.176 0 0 1-8.93 7.076h-12.52v13.886h12.52a9.174 9.174 0 0 1 8.93 7.076c1.5 6.384 4.02 12.46 7.486 18.056a9.176 9.176 0 0 1-1.31 11.318l-8.86 8.86 9.818 9.818 8.86-8.86a9.176 9.176 0 0 1 11.318-1.312 60.556 60.556 0 0 0 18.056 7.488 9.174 9.174 0 0 1 7.074 8.93l-0.002 12.52z m6.944-32.956c-26.404 0-47.884-21.48-47.884-47.882s21.48-47.884 47.884-47.884c26.402 0 47.882 21.48 47.882 47.884 0 26.402-21.48 47.882-47.882 47.882z m0-77.42c-16.286 0-29.538 13.25-29.538 29.538 0 16.286 13.25 29.536 29.538 29.536s29.536-13.25 29.536-29.536-13.25-29.538-29.536-29.538z" fill="#4C4372" p-id="7729"></path></svg>"""
    return svg_data, 200, {'Content-Type': 'image/svg+xml'}

@bp.route('/', methods=['GET'])
def index():
    """返回页面"""
    try:
        return render_template_string(PAGE_TEMPLATE)
    except Exception as e:
        return f"<h1>错误</h1><p>加载页面失败: {str(e)}</p>", 500

@bp.route('/.api/requests', methods=['GET'])
def request_logs():
    """获取请求日志列表API"""
    try:
        # 解析请求参数
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))
        
        # 获取筛选条件
        start_time = request.args.get('start_time')
        end_time = request.args.get('end_time')
        
        # 获取所有module参数（可能有多个）
        modules = request.args.getlist('module')
        # 如果没有模块参数或者只有一个空模块参数，则设置为None
        if not modules or (len(modules) == 1 and not modules[0]):
            modules = None
        
        status_code = request.args.get('status_code')
        
        # 如果status_code存在且不为空，则转换为整数
        if status_code:
            try:
                status_code = int(status_code)
            except ValueError:
                status_code = None
        
        # 获取符合条件的请求日志总数
        total = get_requests_count(
            start_time=start_time,
            end_time=end_time,
            modules=modules,
            status_code=status_code
        )
        
        # 计算总页数
        total_pages = (total + size - 1) // size  # 向上取整
        
        # 根据筛选条件和分页参数获取请求日志
        paginated_logs = get_all_requests(
            pagesize=size,
            current=page,
            start_time=start_time,
            end_time=end_time,
            modules=modules,
            status_code=status_code
        )
        
        # 返回JSON格式数据
        return render_template_string(LOGS_API_TEMPLATE,
                                    logs=paginated_logs,
                                    page=page,
                                    size=size,
                                    total=total,
                                    total_pages=total_pages)
    except Exception as e:
        return jsonify({
            "errCode": 500,
            "errMsg": "获取请求日志失败: " + str(e),
            "data": None
        }), 500

@bp.route('/.api/modules', methods=['GET'])
def get_modules():
    """获取所有可用的模块列表"""
    try:
        # 调用数据库函数获取所有模块
        modules = get_all_modules()
        
        # 返回JSON格式数据
        return jsonify({
            "errCode": 0,
            "errMsg": "success",
            "data": modules
        })
    except Exception as e:
        return jsonify({
            "errCode": 500,
            "errMsg": "获取模块列表失败: " + str(e),
            "data": None
        }), 500

@bp.route('/.api/requests/<request_id>', methods=['GET'])
def request_detail(request_id):
    """获取单个请求的详细信息"""
    try:
        # 获取指定请求日志
        log = get_request_by_id(request_id)
        
        if log is None:
            return jsonify({
                "errCode": 404,
                "errMsg": "请求日志未找到",
                "data": None
            }), 404
        
        # 返回JSON格式的详细信息
        return render_template_string(REQUEST_DETAIL_TEMPLATE, log=log)
    except Exception as e:
        return jsonify({
            "errCode": 500,
            "errMsg": "获取请求日志详情失败: " + str(e),
            "data": None
        }), 500