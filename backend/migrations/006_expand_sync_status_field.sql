-- 扩大 sync_status 字段长度以存储完整的错误信息
-- Migration: 006_expand_sync_status_field

-- PRD 文档表
ALTER TABLE prd_documents 
ALTER COLUMN sync_status TYPE TEXT;

-- 测试用例表
ALTER TABLE test_cases 
ALTER COLUMN sync_status TYPE TEXT;
