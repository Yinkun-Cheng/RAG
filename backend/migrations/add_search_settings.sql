-- ============================================
-- 添加搜索配置到 global_settings 表
-- ============================================

-- 插入搜索相关配置
INSERT INTO global_settings (id, key, value, type, description, created_at) VALUES
('gs-5', 'search_default_alpha', '1.0', 'number', '默认混合检索权重 (0=纯BM25, 1=纯向量, 0.5=各占50%)', CURRENT_TIMESTAMP),
('gs-6', 'search_default_limit', '10', 'number', '默认搜索结果数量限制', CURRENT_TIMESTAMP),
('gs-7', 'search_default_threshold', '0.7', 'number', '默认相似度阈值', CURRENT_TIMESTAMP),
('gs-8', 'search_enable_hybrid', 'true', 'boolean', '是否启用混合检索功能', CURRENT_TIMESTAMP)
ON CONFLICT (key) DO NOTHING;

-- 更新说明
COMMENT ON TABLE global_settings IS '全局配置表（存储 Embedding API、搜索配置等全局配置）';
