package postgres

import (
	"rag-backend/internal/domain/project"

	"gorm.io/gorm"
)

// ModuleRepository 模块仓储接口
type ModuleRepository interface {
	Create(module *project.Module) error
	GetByID(id string) (*project.Module, error)
	GetTree(projectID string) ([]*project.Module, error)
	Update(module *project.Module) error
	Delete(id string) error
	UpdateSortOrder(modules []project.Module) error
	GetChildren(parentID string) ([]*project.Module, error)
}

type moduleRepository struct {
	db *gorm.DB
}

// NewModuleRepository 创建模块仓储实例
func NewModuleRepository(db *gorm.DB) ModuleRepository {
	return &moduleRepository{db: db}
}

// Create 创建模块
func (r *moduleRepository) Create(module *project.Module) error {
	return r.db.Create(module).Error
}

// GetByID 根据 ID 获取模块
func (r *moduleRepository) GetByID(id string) (*project.Module, error) {
	var module project.Module
	err := r.db.Where("id = ?", id).First(&module).Error
	if err != nil {
		return nil, err
	}
	return &module, nil
}

// GetTree 获取模块树（递归查询所有模块）
func (r *moduleRepository) GetTree(projectID string) ([]*project.Module, error) {
	var modules []*project.Module
	
	// 查询所有模块，按 sort_order 排序
	err := r.db.Where("project_id = ?", projectID).
		Order("sort_order ASC, created_at ASC").
		Find(&modules).Error
	
	if err != nil {
		return nil, err
	}

	// 构建树形结构
	return buildTree(modules, nil), nil
}

// buildTree 构建树形结构
func buildTree(modules []*project.Module, parentID *string) []*project.Module {
	var tree []*project.Module
	
	for _, module := range modules {
		// 匹配父节点
		if (parentID == nil && module.ParentID == nil) || 
		   (parentID != nil && module.ParentID != nil && *module.ParentID == *parentID) {
			// 递归查找子节点
			module.Children = buildTree(modules, &module.ID)
			tree = append(tree, module)
		}
	}
	
	return tree
}

// Update 更新模块
func (r *moduleRepository) Update(module *project.Module) error {
	return r.db.Save(module).Error
}

// Delete 删除模块（软删除）
func (r *moduleRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&project.Module{}).Error
}

// UpdateSortOrder 批量更新排序
func (r *moduleRepository) UpdateSortOrder(modules []project.Module) error {
	return r.db.Transaction(func(tx *gorm.DB) error {
		for _, module := range modules {
			if err := tx.Model(&project.Module{}).
				Where("id = ?", module.ID).
				Update("sort_order", module.SortOrder).Error; err != nil {
				return err
			}
		}
		return nil
	})
}

// GetChildren 获取子模块
func (r *moduleRepository) GetChildren(parentID string) ([]*project.Module, error) {
	var modules []*project.Module
	err := r.db.Where("parent_id = ?", parentID).
		Order("sort_order ASC").
		Find(&modules).Error
	return modules, err
}
