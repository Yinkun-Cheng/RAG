package testcase

import (
	"time"
)

// TestStepScreenshot 测试步骤截图模型
type TestStepScreenshot struct {
	ID         string    `gorm:"type:varchar(36);primaryKey" json:"id"`
	TestStepID string    `gorm:"type:varchar(36);not null;index" json:"test_step_id"`
	FileName   string    `gorm:"type:varchar(255);not null" json:"file_name"`
	FilePath   string    `gorm:"type:varchar(500);not null" json:"file_path"`
	FileURL    string    `gorm:"type:varchar(500);not null" json:"file_url"`
	FileSize   int64     `gorm:"not null" json:"file_size"`
	MimeType   string    `gorm:"type:varchar(100);not null" json:"mime_type"`
	SortOrder  int       `gorm:"default:0;index" json:"sort_order"`
	CreatedAt  time.Time `gorm:"not null;default:CURRENT_TIMESTAMP" json:"created_at"`

	// 关联
	TestStep *TestStep `gorm:"foreignKey:TestStepID" json:"test_step,omitempty"`
}

// TableName 指定表名
func (TestStepScreenshot) TableName() string {
	return "test_step_screenshots"
}
