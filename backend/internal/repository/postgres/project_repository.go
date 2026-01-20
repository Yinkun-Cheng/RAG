package postgres

import (
	"rag-backend/internal/domain/project"

	"gorm.io/gorm"
)

// ProjectRepository 项目仓储接口
type ProjectRepository interface {
	Create(proj *project.Project) error
	GetByID(id string) (*project.Project, error)
	List(page, pageSize int) ([]*project.Project, int64, error)
	Update(proj *project.Project) error
	Delete(id string) error
	GetStatistics(id string) (map[string]interface{}, error)
}

type projectRepository struct {
	db *gorm.DB
}

// NewProjectRepository 创建项目仓储实例
func NewProjectRepository(db *gorm.DB) ProjectRepository {
	return &projectRepository{db: db}
}

// Create 创建项目
func (r *projectRepository) Create(proj *project.Project) error {
	return r.db.Create(proj).Error
}

// GetByID 根据 ID 获取项目
func (r *projectRepository) GetByID(id string) (*project.Project, error) {
	var proj project.Project
	err := r.db.Where("id = ?", id).First(&proj).Error
	if err != nil {
		return nil, err
	}
	return &proj, nil
}

// List 获取项目列表
func (r *projectRepository) List(page, pageSize int) ([]*project.Project, int64, error) {
	var projects []*project.Project
	var total int64

	// 计算总数
	if err := r.db.Model(&project.Project{}).Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 分页查询
	offset := (page - 1) * pageSize
	err := r.db.Offset(offset).Limit(pageSize).Order("created_at DESC").Find(&projects).Error
	if err != nil {
		return nil, 0, err
	}

	return projects, total, nil
}

// Update 更新项目
func (r *projectRepository) Update(proj *project.Project) error {
	return r.db.Save(proj).Error
}

// Delete 删除项目（软删除）
func (r *projectRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&project.Project{}).Error
}

// GetStatistics 获取项目统计信息
func (r *projectRepository) GetStatistics(id string) (map[string]interface{}, error) {
	stats := make(map[string]interface{})

	// 统计 PRD 数量
	var prdCount int64
	if err := r.db.Table("prd_documents").Where("project_id = ? AND deleted_at IS NULL", id).Count(&prdCount).Error; err != nil {
		return nil, err
	}
	stats["prd_count"] = prdCount

	// 统计测试用例数量
	var testCaseCount int64
	if err := r.db.Table("test_cases").Where("project_id = ? AND deleted_at IS NULL", id).Count(&testCaseCount).Error; err != nil {
		return nil, err
	}
	stats["test_case_count"] = testCaseCount

	// 统计模块数量
	var moduleCount int64
	if err := r.db.Table("modules").Where("project_id = ? AND deleted_at IS NULL", id).Count(&moduleCount).Error; err != nil {
		return nil, err
	}
	stats["module_count"] = moduleCount

	// 统计标签数量
	var tagCount int64
	if err := r.db.Table("tags").Where("project_id = ? AND deleted_at IS NULL", id).Count(&tagCount).Error; err != nil {
		return nil, err
	}
	stats["tag_count"] = tagCount

	return stats, nil
}
