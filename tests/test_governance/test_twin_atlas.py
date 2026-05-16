"""
Twin Atlas Tests
"""

import pytest
from taiji_verify.governance.twin_atlas import TwinAtlas, AtlasResult


class TestTwinAtlas:
    """双图测试"""

    def test_forward_routing(self):
        """测试正向路由"""
        atlas = TwinAtlas()
        result = atlas.forward_route("碳排放权交易分析")
        assert result.target_domain is not None

    def test_inverse_validation(self):
        """测试逆向验证"""
        atlas = TwinAtlas()
        result = atlas.inverse_validate("有效的问题描述")
        assert isinstance(result.is_valid, bool)

    def test_full_atlas_execution(self):
        """测试完整双图执行"""
        atlas = TwinAtlas()
        result = atlas.execute("碳排放权交易分析")
        assert result.forward_result is not None
        assert result.inverse_result is not None
