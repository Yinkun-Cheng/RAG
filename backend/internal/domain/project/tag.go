package project

import (
	"rag-backend/internal/domain/common"
)

// Tag 标签模型
type Tag struct {
	common.BaseModel
	ProjectID   string `gorm:"type:varchar(36);not null;index" json:"project_id"`
	Name        string `gorm:"type:varchar(50);not null" json:"name"`
	Color       string `gorm:"type:varchar(20)" json:"color"`
	Description string `gorm:"type:text" json:"description"`

	// 关联
	Project *Project `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
}

// TableName 指定表名
func (Tag) TableName() string {
	return "tags"
}
