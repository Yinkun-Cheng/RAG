package prd

import (
	"errors"
	"time"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/prd"
	"rag-backend/internal/repository/postgres"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Service PRD 文档服务接口
type Service interface {
	CreatePRD(projectID string, req *CreatePRDRequest) (*prd.PRDDocument, error)
	GetPRD(id string) (*prd.PRDDocument, error)
	ListPRDs(projectID string, req *ListPRDRequest) (*ListPRDResponse, error)
	UpdatePRD(id string, req *UpdatePRDRequest) (*prd.PRDDocument, error)
	DeletePRD(id string) error
}

type service struct {
	repo postgres.PRDRepository
}

// NewService 创建 PRD 文档服务实例
func NewService(repo postgres.PRDRepository) Service {
	return &service{repo: repo}
}

// CreatePRDRequest 创建 PRD 请求
type CreatePRDRequest struct {
	AppVersionID string  `json:"app_version_id" binding:"required"`
	Code         string  `json:"code" binding:"required,max=50"`
	Title        string  `json:"title" binding:"required,max=200"`
	ModuleID     *string `json:"module_id"`
	Content      string  `json:"content" binding:"required"`
	Author       string  `json:"author" binding:"max=100"`
}

// UpdatePRDRequest 更新 PRD 请求
type UpdatePRDRequest struct {
	AppVersionID *string `json:"app_version_id"`
	Title        *string `json:"title" binding:"omitempty,max=200"`
	ModuleID     *string `json:"module_id"`
	Content      *string `json:"content"`
	Status       *string `json:"status" binding:"omitempty,oneof=draft published archived"`
	Author       *string `json:"author" binding:"omitempty,max=100"`
}

// ListPRDRequest 获取 PRD 列表请求
type ListPRDRequest struct {
	ModuleID     *string  `form:"module_id"`
	Status       *string  `form:"status"`
	AppVersionID *string  `form:"app_version_id"`
	TagIDs       []string `form:"tag_ids"`
	Keyword      *string  `form:"keyword"`
	Page         int      `form:"page" binding:"required,min=1"`
	PageSize     int      `form:"page_size" binding:"required,min=1,max=100"`
}

// ListPRDResponse 获取 PRD 列表响应
type ListPRDResponse struct {
	Items      []*prd.PRDDocument `json:"items"`
	Total      int64              `json:"total"`
	Page       int                `json:"page"`
	PageSize   int                `json:"page_size"`
	TotalPages int                `json:"total_pages"`
}

// CreatePRD 创建 PRD 文档
func (s *service) CreatePRD(projectID string, req *CreatePRDRequest) (*prd.PRDDocument, error) {
	// 检查编号是否已存在
	existing, err := s.repo.GetByCode(projectID, req.Code)
	if err == nil && existing != nil {
		return nil, errors.New("PRD code already exists")
	}
	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, err
	}

	now := time.Now()
	doc := &prd.PRDDocument{
		BaseModel: common.BaseModel{
			ID: uuid.New().String(),
		},
		ProjectID:      projectID,
		AppVersionID:   req.AppVersionID,
		Code:           req.Code,
		Title:          req.Title,
		ModuleID:       req.ModuleID,
		Content:        req.Content,
		Status:         "draft",
		Version:        1,
		Author:         req.Author,
		SyncedToVector: false,
		SyncStatus:     nil,
		LastSyncedAt:   &now,
	}

	if err := s.repo.Create(doc); err != nil {
		return nil, err
	}

	// 重新查询以获取关联数据
	return s.repo.GetByID(doc.ID)
}

// GetPRD 获取 PRD 文档详情
func (s *service) GetPRD(id string) (*prd.PRDDocument, error) {
	doc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}
	return doc, nil
}

// ListPRDs 获取 PRD 文档列表
func (s *service) ListPRDs(projectID string, req *ListPRDRequest) (*ListPRDResponse, error) {
	params := &postgres.PRDListParams{
		ProjectID:    projectID,
		ModuleID:     req.ModuleID,
		Status:       req.Status,
		AppVersionID: req.AppVersionID,
		TagIDs:       req.TagIDs,
		Keyword:      req.Keyword,
		Page:         req.Page,
		PageSize:     req.PageSize,
	}

	docs, total, err := s.repo.List(params)
	if err != nil {
		return nil, err
	}

	totalPages := int(total) / req.PageSize
	if int(total)%req.PageSize > 0 {
		totalPages++
	}

	return &ListPRDResponse{
		Items:      docs,
		Total:      total,
		Page:       req.Page,
		PageSize:   req.PageSize,
		TotalPages: totalPages,
	}, nil
}

// UpdatePRD 更新 PRD 文档
func (s *service) UpdatePRD(id string, req *UpdatePRDRequest) (*prd.PRDDocument, error) {
	doc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	// 更新字段
	if req.AppVersionID != nil {
		doc.AppVersionID = *req.AppVersionID
	}
	if req.Title != nil {
		doc.Title = *req.Title
	}
	if req.ModuleID != nil {
		doc.ModuleID = req.ModuleID
	}
	if req.Content != nil {
		doc.Content = *req.Content
		// 内容更新后，版本号加 1
		doc.Version++
		// 标记需要重新同步
		doc.SyncedToVector = false
	}
	if req.Status != nil {
		doc.Status = *req.Status
	}
	if req.Author != nil {
		doc.Author = *req.Author
	}

	if err := s.repo.Update(doc); err != nil {
		return nil, err
	}

	// 重新查询以获取关联数据
	return s.repo.GetByID(doc.ID)
}

// DeletePRD 删除 PRD 文档
func (s *service) DeletePRD(id string) error {
	// 检查是否存在
	_, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("PRD not found")
		}
		return err
	}

	return s.repo.Delete(id)
}
