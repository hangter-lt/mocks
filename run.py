from app import create_app
from app.modules import REGISTERED_MODULES
print("=== 应用启动初始化 ===")
print("正在创建Flask应用实例...")

# 创建模块级别的Flask应用实例，供gunicorn使用
app = create_app()

# 显示模块加载信息
print("\n=== 功能模块加载信息 ===")
print(f"成功加载的模块数量: {len(REGISTERED_MODULES)}")
print(f"成功加载的模块列表: {', '.join(REGISTERED_MODULES.keys())}")

# 显示每个模块的详细信息
print("\n=== 模块详细信息 ===")
for name, blueprint in REGISTERED_MODULES.items():
    print(f"- 模块名称: {name}")
    print(f"  URL前缀: {blueprint.url_prefix}")
    print(f"  注册的路由数量: {len(blueprint.deferred_functions)}")


def main():
    """主函数"""
    print("\n=== 应用启动信息 ===")
    print("\n✓ 应用已成功启动！")
    
    # 启动Flask服务
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()