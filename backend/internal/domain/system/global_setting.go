package system

import (
	"time"
)

// GlobalSetting 全局配置模型
type GlobalSetting struct {
	ID          string    `gorm:"column:id;primaryKey" json:"id"`
	Key         string    `gorm:"column:key;uniqueIndex;not null" json:"key"`
	Value       string    `gorm:"column:value;type:text" json:"value"`
	Type        string    `gorm:"column:type;not null;default:string" json:"type"`
	Description string    `gorm:"column:description;type:text" json:"description"`
	CreatedAt   time.Time `gorm:"column:created_at;not null;autoCreateTime" json:"created_at"`
	UpdatedAt   time.Time `gorm:"column:updated_at;not null;autoUpdateTime" json:"updated_at"`
}

// TableName 指定表名
func (GlobalSetting) TableName() string {
	return "global_settings"
}
