package testcase

import (
	"time"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/prd"
	"rag-backend/internal/domain/project"
)

// TestCase 测试用例模型
type TestCase struct {
	common.BaseModel
	ProjectID      string     `gorm:"type:varchar(36);not null;index" json:"project_id"`
	AppVersionID   string     `gorm:"type:varchar(36);not null;index" json:"app_version_id"`
	Code           string     `gorm:"type:varchar(50);not null;index" json:"code"`
	Title          string     `gorm:"type:varchar(200);not null" json:"title"`
	PRDID          *string    `gorm:"type:varchar(36);index" json:"prd_id"`
	ModuleID       *string    `gorm:"type:varchar(36);index" json:"module_id"`
	Precondition   string     `gorm:"type:text" json:"precondition"`
	ExpectedResult string     `gorm:"type:text;not null" json:"expected_result"`
	Priority       string     `gorm:"type:varchar(10);not null;default:'medium';index" json:"priority"`
	Type           string     `gorm:"type:varchar(50);not null;default:'functional';index" json:"type"`
	Status         string     `gorm:"type:varchar(20);not null;default:'active';index" json:"status"`
	Version        int        `gorm:"not null;default:1" json:"version"`
	SyncedToVector bool       `gorm:"default:false" json:"synced_to_vector"`
	SyncStatus     *string    `gorm:"type:varchar(20);index" json:"sync_status"`
	LastSyncedAt   *time.Time `json:"last_synced_at"`

	// 关联
	Project    *project.Project    `gorm:"foreignKey:ProjectID" json:"project,omitempty"`
	AppVersion *project.AppVersion `gorm:"foreignKey:AppVersionID" json:"app_version,omitempty"`
	PRD        *prd.PRDDocument    `gorm:"foreignKey:PRDID" json:"prd,omitempty"`
	Module     *project.Module     `gorm:"foreignKey:ModuleID" json:"module,omitempty"`
	Tags       []*project.Tag      `gorm:"many2many:test_case_tags" json:"tags,omitempty"`
	Steps      []*TestStep         `gorm:"foreignKey:TestCaseID;constraint:OnDelete:CASCADE" json:"steps,omitempty"`
	Versions   []*TestCaseVersion  `gorm:"foreignKey:TestCaseID" json:"versions,omitempty"`
}

// TableName 指定表名
func (TestCase) TableName() string {
	return "test_cases"
}
