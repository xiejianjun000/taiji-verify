"""
Taiji Verify 插件系统 (可选集成)

⚠️ 注意：此模块依赖 taiji_agent.plugin_system，在独立 taiji-verify 项目中无法直接使用。

此文件保留在 contrib/ 目录作为可选集成示例：
- 当与 taiji-agent 一起使用时，可导入此模块获得插件能力
- 独立使用时，忽略此文件即可

用法（在与 taiji-agent 集成时）：
    from taiji_verify.contrib.plugins import TaijiVerifyPlugin
"""

# 此模块需要 taiji-agent 仓库中的以下模块:
# from taiji_agent.plugin_system import Plugin, PluginConfig, PluginMetadata, PluginState
# from taiji_agent.event_bus import EventBus, Event, EventType, get_event_bus

# 条件导入以避免独立项目报错
try:
    from taiji_agent.plugin_system import Plugin, PluginConfig, PluginMetadata, PluginState
    from taiji_agent.event_bus import EventBus, Event, EventType, get_event_bus
    TAIJI_AGENT_AVAILABLE = True
except ImportError:
    TAIJI_AGENT_AVAILABLE = False
    Plugin = object  # 占位符，避免后续代码直接报错
    PluginConfig = None
    PluginMetadata = None
    PluginState = None
    EventBus = None
    Event = None
    EventType = None
    get_event_bus = None


if TAIJI_AGENT_AVAILABLE:
    class TaijiVerifyPlugin(Plugin):
        """
        太极验证插件 - 与 taiji-agent 集成时使用
        
        提供:
        - 验证事件发布
        - 验证结果订阅
        - 与其他插件的协调
        """
        
        PLUGIN_NAME = "taiji-verify"
        
        def __init__(self, config: PluginConfig = None):
            super().__init__(config)
            self.verify_engine = None
            self.event_history = []
        
        def on_load(self) -> bool:
            """加载插件时初始化验证引擎"""
            from taiji_verify import TaijiVerifyEngine
            self.verify_engine = TaijiVerifyEngine()
            return True
        
        def on_enable(self) -> bool:
            """启用插件"""
            self._subscribe_to_events()
            return True
        
        def on_disable(self) -> None:
            """禁用插件"""
            self._unsubscribe_from_events()
        
        def _subscribe_to_events(self):
            """订阅事件"""
            bus = get_event_bus()
            if bus:
                bus.subscribe(EventType.OUTPUT_GENERATED, self._on_output_generated)
        
        def _unsubscribe_from_events(self):
            """取消订阅事件"""
            bus = get_event_bus()
            if bus:
                bus.unsubscribe(EventType.OUTPUT_GENERATED, self._on_output_generated)
        
        def _on_output_generated(self, event: Event):
            """处理输出生成事件"""
            if not self.verify_engine:
                return
            
            # 执行验证
            from taiji_verify import VerificationRequest
            request = VerificationRequest(
                input_text=event.data.get('input', ''),
                ground_truth=event.data.get('expected', ''),
                context=event.data.get('context', {})
            )
            
            result = self.verify_engine.verify(request)
            
            # 发布验证结果事件
            result_event = Event(
                event_type=EventType.VERIFICATION_COMPLETED,
                source=self.PLUGIN_NAME,
                data={
                    'verdict': result.verdict,
                    'passed': result.is_passing,
                    'failure_count': result.failure_count,
                }
            )
            
            bus = get_event_bus()
            if bus:
                bus.publish(result_event)
            
            self.event_history.append(result_event)
        
        def get_verification_stats(self) -> dict:
            """获取验证统计"""
            if not self.event_history:
                return {'total': 0, 'passed': 0, 'failed': 0}
            
            passed = sum(1 for e in self.event_history if e.data.get('passed'))
            return {
                'total': len(self.event_history),
                'passed': passed,
                'failed': len(self.event_history) - passed,
                'pass_rate': passed / len(self.event_history) if self.event_history else 0,
            }
