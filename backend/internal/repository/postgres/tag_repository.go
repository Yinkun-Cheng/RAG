package postgres

import (
	"rag-backend/internal/domain/project"

	"gorm.io/gorm"
)

// TagRepository 标签仓储接口
type TagRepository interface {
	Create(tag *project.Tag) error
	GetByID(id string) (*project.Tag, error)
	GetByProjectID(projectID string) ([]*project.Tag, error)
	Update(tag *project.Tag) error
	Delete(id string) error
	GetUsageCount(tagID string) (prdCount int64, testCaseCount int64, err error)
}

type tagRepository struct {
	db *gorm.DB
}

// NewTagRepository 创建标签仓储实例
func NewTagRepository(db *gorm.DB) TagRepository {
	return &tagRepository{db: db}
}

// Create 创建标签
func (r *tagRepository) Create(tag *project.Tag) error {
	return r.db.Create(tag).Error
}

// GetByID 根据 ID 获取标签
func (r *tagRepository) GetByID(id string) (*project.Tag, error) {
	var tag project.Tag
	err := r.db.Where("id = ?", id).First(&tag).Error
	return &tag, err
}

// GetByProjectID 获取项目的所有标签
func (r *tagRepository) GetByProjectID(projectID string) ([]*project.Tag, error) {
	var tags []*project.Tag
	err := r.db.Where("project_id = ?", projectID).
		Order("created_at DESC").
		Find(&tags).Error
	return tags, err
}

// Update 更新标签
func (r *tagRepository) Update(tag *project.Tag) error {
	return r.db.Save(tag).Error
}

// Delete 删除标签（软删除）
func (r *tagRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&project.Tag{}).Error
}

// GetUsageCount 获取标签使用统计
func (r *tagRepository) GetUsageCount(tagID string) (prdCount int64, testCaseCount int64, err error) {
	// 统计 PRD 使用数量
	err = r.db.Table("prd_tags").
		Where("tag_id = ?", tagID).
		Count(&prdCount).Error
	if err != nil {
		return 0, 0, err
	}

	// 统计测试用例使用数量
	err = r.db.Table("test_case_tags").
		Where("tag_id = ?", tagID).
		Count(&testCaseCount).Error
	if err != nil {
		return 0, 0, err
	}

	return prdCount, testCaseCount, nil
}
