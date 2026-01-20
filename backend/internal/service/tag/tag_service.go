package tag

import (
	"errors"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"
	"rag-backend/internal/repository/postgres"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Service 标签服务接口
type Service interface {
	CreateTag(projectID string, req *CreateTagRequest) (*project.Tag, error)
	GetTags(projectID string) ([]*project.Tag, error)
	GetTagByID(id string) (*project.Tag, error)
	UpdateTag(id string, req *UpdateTagRequest) (*project.Tag, error)
	DeleteTag(id string) error
	GetTagUsage(id string) (*TagUsageResponse, error)
}

type service struct {
	repo postgres.TagRepository
}

// NewService 创建标签服务实例
func NewService(repo postgres.TagRepository) Service {
	return &service{repo: repo}
}

// CreateTagRequest 创建标签请求
type CreateTagRequest struct {
	Name        string `json:"name" binding:"required,max=50"`
	Color       string `json:"color" binding:"max=20"`
	Description string `json:"description"`
}

// UpdateTagRequest 更新标签请求
type UpdateTagRequest struct {
	Name        string `json:"name" binding:"max=50"`
	Color       string `json:"color" binding:"max=20"`
	Description string `json:"description"`
}

// TagUsageResponse 标签使用统计响应
type TagUsageResponse struct {
	TagID         string `json:"tag_id"`
	TagName       string `json:"tag_name"`
	PRDCount      int64  `json:"prd_count"`
	TestCaseCount int64  `json:"test_case_count"`
	TotalCount    int64  `json:"total_count"`
}

// CreateTag 创建标签
func (s *service) CreateTag(projectID string, req *CreateTagRequest) (*project.Tag, error) {
	tag := &project.Tag{
		BaseModel: common.BaseModel{
			ID: uuid.New().String(),
		},
		ProjectID:   projectID,
		Name:        req.Name,
		Color:       req.Color,
		Description: req.Description,
	}

	if err := s.repo.Create(tag); err != nil {
		return nil, err
	}

	return tag, nil
}

// GetTags 获取项目的所有标签
func (s *service) GetTags(projectID string) ([]*project.Tag, error) {
	return s.repo.GetByProjectID(projectID)
}

// GetTagByID 根据 ID 获取标签
func (s *service) GetTagByID(id string) (*project.Tag, error) {
	tag, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("tag not found")
		}
		return nil, err
	}
	return tag, nil
}

// UpdateTag 更新标签
func (s *service) UpdateTag(id string, req *UpdateTagRequest) (*project.Tag, error) {
	tag, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("tag not found")
		}
		return nil, err
	}

	if req.Name != "" {
		tag.Name = req.Name
	}
	if req.Color != "" {
		tag.Color = req.Color
	}
	if req.Description != "" {
		tag.Description = req.Description
	}

	if err := s.repo.Update(tag); err != nil {
		return nil, err
	}

	return tag, nil
}

// DeleteTag 删除标签
func (s *service) DeleteTag(id string) error {
	// 检查标签是否存在
	_, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("tag not found")
		}
		return err
	}

	// 检查标签是否被使用
	prdCount, testCaseCount, err := s.repo.GetUsageCount(id)
	if err != nil {
		return err
	}

	if prdCount > 0 || testCaseCount > 0 {
		return errors.New("cannot delete tag that is in use")
	}

	return s.repo.Delete(id)
}

// GetTagUsage 获取标签使用统计
func (s *service) GetTagUsage(id string) (*TagUsageResponse, error) {
	tag, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("tag not found")
		}
		return nil, err
	}

	prdCount, testCaseCount, err := s.repo.GetUsageCount(id)
	if err != nil {
		return nil, err
	}

	return &TagUsageResponse{
		TagID:         tag.ID,
		TagName:       tag.Name,
		PRDCount:      prdCount,
		TestCaseCount: testCaseCount,
		TotalCount:    prdCount + testCaseCount,
	}, nil
}
