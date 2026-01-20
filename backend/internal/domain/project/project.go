package project

import (
	"rag-backend/internal/domain/common"
)

// Project 项目模型
type Project struct {
	common.BaseModel
	Name        string `gorm:"type:varchar(100);not null" json:"name"`
	Description string `gorm:"type:text" json:"description"`
}

// TableName 指定表名
func (Project) TableName() string {
	return "projects"
}
