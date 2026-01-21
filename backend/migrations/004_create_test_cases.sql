-- 创建测试用例表
CREATE TABLE IF NOT EXISTS test_cases (
    id VARCHAR(36) PRIMARY KEY DEFAULT gen_random_uuid()::VARCH