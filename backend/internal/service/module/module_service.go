package module

import (
	"errors"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"
	"rag-backend/internal/repository/postgres"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Service 模块服务接口
type Service interface {
	CreateModule(projectID string, req *CreateModuleRequest) (*project.Module, error)
	GetModuleTree(projectID string) ([]*project.Module, error)
	UpdateModule(id string, req *UpdateModuleRequest) (*project.Module, error)
	DeleteModule(id string) error
	SortModules(projectID string, req *SortModulesRequest) error
}

type service struct {
	repo postgres.ModuleRepository
}

// NewService 创建模块服务实例
func NewService(repo postgres.ModuleRepository) Service {
	return &service{repo: repo}
}

// CreateModuleRequest 创建模块请求
type CreateModuleRequest struct {
	Name        string  `json:"name" binding:"required,max=100"`
	Description string  `json:"description"`
	ParentID    *string `json:"parent_id"`
	SortOrder   int     `json:"sort_order"`
}

// UpdateModuleRequest 更新模块请求
type UpdateModuleRequest struct {
	Name        string  `json:"name" binding:"max=100"`
	Description string  `json:"description"`
	ParentID    *string `json:"parent_id"`
	SortOrder   *int    `json:"sort_order"`
}

// SortModulesRequest 排序请求
type SortModulesRequest struct {
	Modules []ModuleSortItem `json:"modules" binding:"required"`
}

// ModuleSortItem 排序项
type ModuleSortItem struct {
	ID        string `json:"id" binding:"required"`
	SortOrder int    `json:"sort_order"`
}

// CreateModule 创建模块
func (s *service) CreateModule(projectID string, req *CreateModuleRequest) (*project.Module, error) {
	// 验证父模块是否存在
	if req.ParentID != nil && *req.ParentID != "" {
		_, err := s.repo.GetByID(*req.ParentID)
		if err != nil {
			if errors.Is(err, gorm.ErrRecordNotFound) {
				return nil, errors.New("parent module not found")
			}
			return nil, err
		}
	}

	module := &project.Module{
		BaseModel: common.BaseModel{
			ID: uuid.New().String(),
		},
		ProjectID:   projectID,
		Name:        req.Name,
		Description: req.Description,
		ParentID:    req.ParentID,
		SortOrder:   req.SortOrder,
	}

	if err := s.repo.Create(module); err != nil {
		return nil, err
	}

	return module, nil
}

// GetModuleTree 获取模块树
func (s *service) GetModuleTree(projectID string) ([]*project.Module, error) {
	return s.repo.GetTree(projectID)
}

// UpdateModule 更新模块
func (s *service) UpdateModule(id string, req *UpdateModuleRequest) (*project.Module, error) {
	module, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("module not found")
		}
		return nil, err
	}

	// 验证父模块
	if req.ParentID != nil {
		// 不能将自己设置为父模块
		if *req.ParentID == id {
			return nil, errors.New("cannot set self as parent")
		}

		// 验证父模块是否存在
		if *req.ParentID != "" {
			_, err := s.repo.GetByID(*req.ParentID)
			if err != nil {
				if errors.Is(err, gorm.ErrRecordNotFound) {
					return nil, errors.New("parent module not found")
				}
				return nil, err
			}
		}
		module.ParentID = req.ParentID
	}

	if req.Name != "" {
		module.Name = req.Name
	}
	if req.Description != "" {
		module.Description = req.Description
	}
	if req.SortOrder != nil {
		module.SortOrder = *req.SortOrder
	}

	if err := s.repo.Update(module); err != nil {
		return nil, err
	}

	return module, nil
}

// DeleteModule 删除模块
func (s *service) DeleteModule(id string) error {
	// 检查是否存在
	_, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("module not found")
		}
		return err
	}

	// 检查是否有子模块
	children, err := s.repo.GetChildren(id)
	if err != nil {
		return err
	}
	if len(children) > 0 {
		return errors.New("cannot delete module with children")
	}

	return s.repo.Delete(id)
}

// SortModules 批量排序
func (s *service) SortModules(projectID string, req *SortModulesRequest) error {
	var modules []project.Module
	for _, item := range req.Modules {
		modules = append(modules, project.Module{
			BaseModel: common.BaseModel{ID: item.ID},
			SortOrder: item.SortOrder,
		})
	}

	return s.repo.UpdateSortOrder(modules)
}
