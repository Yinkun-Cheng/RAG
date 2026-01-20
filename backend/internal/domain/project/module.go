package project

import (
	"rag-backend/internal/domain/common"
)

// Module 功能模块模型（树形结构）
type Module struct {
	common.BaseModel
	ProjectID   string  `gorm:"type:varchar(36);not null;index" json:"project_id"`
	Name        string  `gorm:"type:varchar(100);not null" json:"name"`
	Description string  `gorm:"type:text" json:"description"`
	ParentID    *string `gorm:"type:varchar(36);index" json:"parent_id"`
	SortOrder   int     `gorm:"default:0;index" json:"sort_order"`

	// 关联
	Project  *Project  `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
	Parent   *Module   `gorm:"foreignKey:ParentID" json:"parent,omitempty"`
	Children []*Module `gorm:"foreignKey:ParentID" json:"children,omitempty"`
}

// TableName 指定表名
func (Module) TableName() string {
	return "modules"
}
