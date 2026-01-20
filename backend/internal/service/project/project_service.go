package project

import (
	"errors"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"
	"rag-backend/internal/repository/postgres"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Service 项目服务接口
type Service interface {
	CreateProject(req *CreateProjectRequest) (*project.Project, error)
	GetProject(id string) (*project.Project, error)
	ListProjects(page, pageSize int) ([]*project.Project, int64, error)
	UpdateProject(id string, req *UpdateProjectRequest) (*project.Project, error)
	DeleteProject(id string) error
	GetProjectStatistics(id string) (map[string]interface{}, error)
}

type service struct {
	repo postgres.ProjectRepository
}

// NewService 创建项目服务实例
func NewService(repo postgres.ProjectRepository) Service {
	return &service{repo: repo}
}

// CreateProjectRequest 创建项目请求
type CreateProjectRequest struct {
	Name        string `json:"name" binding:"required,max=100"`
	Description string `json:"description"`
}

// UpdateProjectRequest 更新项目请求
type UpdateProjectRequest struct {
	Name        string `json:"name" binding:"max=100"`
	Description string `json:"description"`
}

// CreateProject 创建项目
func (s *service) CreateProject(req *CreateProjectRequest) (*project.Project, error) {
	proj := &project.Project{
		BaseModel: common.BaseModel{
			ID: uuid.New().String(),
		},
		Name:        req.Name,
		Description: req.Description,
	}

	if err := s.repo.Create(proj); err != nil {
		return nil, err
	}

	return proj, nil
}

// GetProject 获取项目
func (s *service) GetProject(id string) (*project.Project, error) {
	proj, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("project not found")
		}
		return nil, err
	}
	return proj, nil
}

// ListProjects 获取项目列表
func (s *service) ListProjects(page, pageSize int) ([]*project.Project, int64, error) {
	if page < 1 {
		page = 1
	}
	if pageSize < 1 || pageSize > 100 {
		pageSize = 10
	}

	return s.repo.List(page, pageSize)
}

// UpdateProject 更新项目
func (s *service) UpdateProject(id string, req *UpdateProjectRequest) (*project.Project, error) {
	proj, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("project not found")
		}
		return nil, err
	}

	if req.Name != "" {
		proj.Name = req.Name
	}
	if req.Description != "" {
		proj.Description = req.Description
	}

	if err := s.repo.Update(proj); err != nil {
		return nil, err
	}

	return proj, nil
}

// DeleteProject 删除项目
func (s *service) DeleteProject(id string) error {
	_, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("project not found")
		}
		return err
	}

	return s.repo.Delete(id)
}

// GetProjectStatistics 获取项目统计信息
func (s *service) GetProjectStatistics(id string) (map[string]interface{}, error) {
	_, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("project not found")
		}
		return nil, err
	}

	return s.repo.GetStatistics(id)
}
