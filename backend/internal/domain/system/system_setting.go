package system

import (
	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"
)

// SystemSetting 系统配置模型
type SystemSetting struct {
	common.BaseModel
	ProjectID    string `gorm:"type:varchar(36);not null;index" json:"project_id"`
	SettingKey   string `gorm:"type:varchar(100);not null;index" json:"setting_key"`
	SettingValue string `gorm:"type:text" json:"setting_value"`
	SettingType  string `gorm:"type:varchar(50);not null;default:'string'" json:"setting_type"`
	Description  string `gorm:"type:text" json:"description"`

	// 关联
	Project *project.Project `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
}

// TableName 指定表名
func (SystemSetting) TableName() string {
	return "system_settings"
}
