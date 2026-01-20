package project

import (
	"rag-backend/internal/domain/common"
)

// AppVersion App 版本模型
type AppVersion struct {
	common.BaseModel
	ProjectID   string `gorm:"type:varchar(36);not null;index" json:"project_id"`
	Version     string `gorm:"type:varchar(50);not null" json:"version"`
	Description string `gorm:"type:text" json:"description"`

	// 关联
	Project *Project `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
}

// TableName 指定表名
func (AppVersion) TableName() string {
	return "app_versions"
}
