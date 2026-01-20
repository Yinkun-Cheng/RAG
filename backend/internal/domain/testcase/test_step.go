package testcase

import (
	"time"
)

// TestStep 测试步骤模型
type TestStep struct {
	ID          string     `gorm:"type:varchar(36);primaryKey" json:"id"`
	TestCaseID  string     `gorm:"type:varchar(36);not null;index" json:"test_case_id"`
	StepOrder   int        `gorm:"not null;index" json:"step_order"`
	Description string     `gorm:"type:text;not null" json:"description"`
	TestData    *string    `gorm:"type:text" json:"test_data"`
	Expected    *string    `gorm:"type:text" json:"expected"`
	CreatedAt   time.Time  `gorm:"not null;default:CURRENT_TIMESTAMP" json:"created_at"`
	UpdatedAt   time.Time  `gorm:"not null;default:CURRENT_TIMESTAMP" json:"updated_at"`

	// 关联
	TestCase    *TestCase             `gorm:"foreignKey:TestCaseID" json:"test_case,omitempty"`
	Screenshots []*TestStepScreenshot `gorm:"foreignKey:TestStepID;constraint:OnDelete:CASCADE" json:"screenshots,omitempty"`
}

// TableName 指定表名
func (TestStep) TableName() string {
	return "test_steps"
}
