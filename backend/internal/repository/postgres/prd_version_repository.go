package postgres

import (
	"rag-backend/internal/domain/prd"

	"gorm.io/gorm"
)

// PRDVersionRepository PRD 版本仓储接口
type PRDVersionRepository interface {
	Create(version *prd.PRDVersion) error
	GetByPRDID(prdID string) ([]*prd.PRDVersion, error)
	GetByVersion(prdID string, version int) (*prd.PRDVersion, error)
	GetLatestVersion(prdID string) (*prd.PRDVersion, error)
}

type prdVersionRepository struct {
	db *gorm.DB
}

// NewPRDVersionRepository 创建 PRD 版本仓储实例
func NewPRDVersionRepository(db *gorm.DB) PRDVersionRepository {
	return &prdVersionRepository{db: db}
}

// Create 创建 PRD 版本记录
func (r *prdVersionRepository) Create(version *prd.PRDVersion) error {
	return r.db.Create(version).Error
}

// GetByPRDID 获取 PRD 的所有版本历史
func (r *prdVersionRepository) GetByPRDID(prdID string) ([]*prd.PRDVersion, error) {
	var versions []*prd.PRDVersion
	err := r.db.Where("prd_id = ?", prdID).
		Order("version DESC").
		Find(&versions).Error
	return versions, err
}

// GetByVersion 获取 PRD 的特定版本
func (r *prdVersionRepository) GetByVersion(prdID string, version int) (*prd.PRDVersion, error) {
	var v prd.PRDVersion
	err := r.db.Where("prd_id = ? AND version = ?", prdID, version).First(&v).Error
	return &v, err
}

// GetLatestVersion 获取 PRD 的最新版本
func (r *prdVersionRepository) GetLatestVersion(prdID string) (*prd.PRDVersion, error) {
	var v prd.PRDVersion
	err := r.db.Where("prd_id = ?", prdID).
		Order("version DESC").
		First(&v).Error
	return &v, err
}
