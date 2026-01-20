package testcase

import (
	"time"

	"gorm.io/datatypes"
)

// TestCaseVersion 测试用例版本历史模型
type TestCaseVersion struct {
	ID             string         `gorm:"type:varchar(36);primaryKey" json:"id"`
	TestCaseID     string         `gorm:"type:varchar(36);not null;index" json:"test_case_id"`
	Version        int            `gorm:"not null;index" json:"version"`
	Title          string         `gorm:"type:varchar(200);not null" json:"title"`
	Precondition   string         `gorm:"type:text" json:"precondition"`
	ExpectedResult string         `gorm:"type:text;not null" json:"expected_result"`
	Priority       string         `gorm:"type:varchar(10);not null" json:"priority"`
	Type           string         `gorm:"type:varchar(50);not null" json:"type"`
	ChangeLog      string         `gorm:"type:text" json:"change_log"`
	Snapshot       datatypes.JSON `gorm:"type:jsonb;not null" json:"snapshot"`
	CreatedBy      string         `gorm:"type:varchar(100)" json:"created_by"`
	CreatedAt      time.Time      `gorm:"not null;default:CURRENT_TIMESTAMP" json:"created_at"`

	// 关联
	TestCase *TestCase `gorm:"foreignKey:TestCaseID" json:"test_case,omitempty"`
}

// TableName 指定表名
func (TestCaseVersion) TableName() string {
	return "test_case_versions"
}
