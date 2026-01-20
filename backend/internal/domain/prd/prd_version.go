package prd

import (
	"time"
)

// PRDVersion PRD 版本历史模型
type PRDVersion struct {
	ID        string    `gorm:"type:varchar(36);primaryKey" json:"id"`
	PRDID     string    `gorm:"type:varchar(36);not null;index" json:"prd_id"`
	Version   int       `gorm:"not null;index" json:"version"`
	Title     string    `gorm:"type:varchar(200);not null" json:"title"`
	Content   string    `gorm:"type:text;not null" json:"content"`
	ChangeLog string    `gorm:"type:text" json:"change_log"`
	CreatedBy string    `gorm:"type:varchar(100)" json:"created_by"`
	CreatedAt time.Time `gorm:"not null;default:CURRENT_TIMESTAMP" json:"created_at"`

	// 关联
	PRD *PRDDocument `gorm:"foreignKey:PRDID" json:"prd,omitempty"`
}

// TableName 指定表名
func (PRDVersion) TableName() string {
	return "prd_versions"
}
