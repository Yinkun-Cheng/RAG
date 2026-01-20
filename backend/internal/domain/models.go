package domain

import (
	"rag-backend/internal/domain/prd"
	"rag-backend/internal/domain/project"
	"rag-backend/internal/domain/system"
	"rag-backend/internal/domain/testcase"
)

// AllModels 返回所有需要迁移的模型
func AllModels() []interface{} {
	return []interface{}{
		// 项目相关
		&project.Project{},
		&project.AppVersion{},
		&project.Module{},
		&project.Tag{},

		// PRD 相关
		&prd.PRDDocument{},
		&prd.PRDVersion{},

		// 测试用例相关
		&testcase.TestCase{},
		&testcase.TestStep{},
		&testcase.TestStepScreenshot{},
		&testcase.TestCaseVersion{},

		// 系统配置
		&system.SystemSetting{},
	}
}
