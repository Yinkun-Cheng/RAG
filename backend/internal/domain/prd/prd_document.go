package prd

import (
	"time"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"
)

// PRDDocument PRD 文档模型
type PRDDocument struct {
	common.BaseModel
	ProjectID      string     `gorm:"type:varchar(36);not null;index" json:"project_id"`
	AppVersionID   string     `gorm:"type:varchar(36);not null;index" json:"app_version_id"`
	Code           string     `gorm:"type:varchar(50);not null;index" json:"code"`
	Title          string     `gorm:"type:varchar(200);not null" json:"title"`
	ModuleID       *string    `gorm:"type:varchar(36);index" json:"module_id"`
	Content        string     `gorm:"type:text;not null" json:"content"`
	Status         string     `gorm:"type:varchar(20);not null;default:'draft';index" json:"status"`
	Version        int        `gorm:"not null;default:1;index" json:"version"`
	Author         string     `gorm:"type:varchar(100)" json:"author"`
	SyncedToVector bool       `gorm:"default:false" json:"synced_to_vector"`
	SyncStatus     *string    `gorm:"type:varchar(20);index" json:"sync_status"`
	LastSyncedAt   *time.Time `json:"last_synced_at"`

	// 关联
	Project    *project.Project    `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
	AppVersion *project.AppVersion `gorm:"foreignKey:AppVersionID" json:"app_version,omitempty"`
	Module     *project.Module     `gorm:"foreignKey:ModuleID" json:"module,omitempty"`
	Tags       []*project.Tag      `gorm:"many2many:prd_tags" json:"tags,omitempty"`
	Versions   []*PRDVersion       `gorm:"foreignKey:PRDID" json:"versions,omitempty"`
}

// TableName 指定表名
func (PRDDocument) TableName() string {
	return "prd_documents"
}
