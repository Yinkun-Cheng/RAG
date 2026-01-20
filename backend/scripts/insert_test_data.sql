-- 为测试项目插入 App 版本数据
-- 项目 ID: 5f6b1548-45fa-4e45-82ef-deaad15a431e

INSERT INTO app_versions (id, project_id, version, description, created_at, updated_at)
VALUES
  ('app-v1-test-001', '5f6b1548-45fa-4e45-82ef-deaad15a431e', 'v1.0.0', '初始版本-基础功能版', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('app-v1-test-002', '5f6b1548-45fa-4e45-82ef-deaad15a431e', 'v1.1.0', '功能优化版本', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
  ('app-v1-test-003', '5f6b1548-45fa-4e45-82ef-deaad15a431e', 'v2.0.0', '架构升级版本', CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
ON CONFLICT (id) DO NOTHING;
