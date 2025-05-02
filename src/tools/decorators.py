"""
工具装饰器模块

提供工具类功能增强组件，包含输入输出日志记录和带日志的工具类创建功能
"""

import logging
import functools
from typing import Any, Callable, Type, TypeVar  # 类型提示支持

# 初始化模块日志记录器
logger = logging.getLogger(__name__)  # 获取当前模块日志实例

# 类型变量定义
T = TypeVar("T")  # 泛型类型占位符


def log_io(func: Callable) -> Callable:
    """
    输入输出日志装饰器
    
    功能：
    1. 记录被装饰函数的输入参数
    2. 记录函数执行结果
    3. 维持函数签名信息
    
    参数:
        func (Callable): 需要增强的日志记录目标函数
        
    返回:
        Callable: 带日志功能增强的包装函数
    """
    
    @functools.wraps(func)  # 保留原始函数元数据
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        """
        包装函数：实现具体的日志记录逻辑
        """
        # 提取函数名称
        func_name = func.__name__
        
        # 格式化参数信息
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]  # 统一参数展示
        )
        
        # 记录调用日志
        logger.debug(f"调用工具函数 {func_name}，参数: {params}")

        # 执行原始函数
        result = func(*args, **kwargs)

        # 记录返回值
        logger.debug(f"工具函数 {func_name} 返回: {result}")

        return result

    return wrapper  # 返回包装后的函数


class LoggedToolMixin:
    """
    工具日志混入类
    
    提供工具类通用日志记录功能
    支持自动记录方法调用和执行结果
    """
    
    def _log_operation(self, method_name: str, *args: Any, **kwargs: Any) -> None:
        """
        操作日志记录器
        
        功能：
        1. 构建工具类名称（去除'Logged'前缀）
        2. 格式化方法调用参数
        3. 记录调试级别日志
        
        参数:
            method_name (str): 被调用的方法名称
            *args: 可变位置参数
            **kwargs: 可变关键字参数
        """
        # 构造实际工具名称
        tool_name = self.__class__.__name__.replace("Logged", "")
        
        # 格式化参数字符串
        params = ", ".join(
            [*(str(arg) for arg in args), *(f"{k}={v}" for k, v in kwargs.items())]
        )
        
        # 记录操作日志
        logger.debug(f"调用工具方法 {tool_name}.{method_name}，参数: {params}")

    def _run(self, *args: Any, **kwargs: Any) -> Any:
        """
        带日志的运行方法
        
        功能：
        1. 调用前记录操作日志
        2. 执行原始_run方法
        3. 记录执行结果日志
        
        参数:
            *args: 可变位置参数
            **kwargs: 可变关键字参数
            
        返回:
            Any: 工具执行结果
        """
        # 记录方法调用
        self._log_operation("_run", *args, **kwargs)
        
        # 执行原始方法
        result = super()._run(*args, **kwargs)
        
        # 记录方法返回值
        logger.debug(
            f"工具类 {self.__class__.__name__.replace('Logged', '')} 返回: {result}"
        )
        
        return result  # 返回执行结果


def create_logged_tool(base_tool_class: Type[T]) -> Type[T]:
    """
    创建带日志的工具类工厂方法
    
    功能：
    1. 接收基础工具类
    2. 构建继承LoggedToolMixin和基础工具的混合类
    3. 返回新的日志增强类
    
    参数:
        base_tool_class (Type[T]): 需要增强的基础工具类
        
    返回:
        Type[T]: 带日志功能的新工具类
    """
    
    class LoggedTool(LoggedToolMixin, base_tool_class):
        """
        带日志功能的工具类
        
        继承关系：LoggedToolMixin + 基础工具类
        实现了自动日志记录的完整工具
        """
        pass

    """
    类名增强
    
    在基础工具类名前添加'Logged'前缀
    用于标识该工具已增强日志功能
    """
    LoggedTool.__name__ = f"Logged{base_tool_class.__name__}"  # 设置可识别的类名
    
    return LoggedTool  # 返回增强后的工具类
