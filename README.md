# 项目框架
+ 使用poetry,虚拟环境，包管理器，隔离python项目
参考链接：https://zhuanlan.zhihu.com/p/445952026
+ fastapi 项目框架
参考链接：https://fastapi.tiangolo.com/zh/

# 项目结构
+ common
中间件(token验证，全局异常捕获，日志等)和其他类型公用文件
+ controller
业务接口的入口逻辑，判断参数调用service层
+ service
service层，业务逻辑，调用mapper层
+ mapper
mysql数据层对接
+ models
使用sqlalchemy的class方式管理mysql表结构
+ untils
公用工具类
+ conf
各种配置文件

# 如何运行
+ 安装poetry(略)
+ 安装依赖项
cd [projectDir]
poetry install
+ 运行(app 是个运行脚本,在pyproject.toml文件中)
poetry run app
