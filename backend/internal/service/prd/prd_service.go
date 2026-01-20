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
	GetPRDVersions(prdID string) ([]*prd.PRDVersion, error)
	GetPRDVersion(prdID string, version int) (*prd.PRDVersion, error)
	ComparePRDVersions(prdID string, version1, version2 int) (*VersionCompareResponse, error)
	UpdatePRDStatus(id string, status string) (*prd.PRDDocument, error)
	PublishPRD(id string) (*prd.PRDDocument, error)
	ArchivePRD(id string) (*prd.PRDDocument, error)
}

type service struct {
	repo        postgres.PRDRepository
	versionRepo postgres.PRDVersionRepository
}

// NewService 创建 PRD 文档服务实例
func NewService(repo postgres.PRDRepository, versionRepo postgres.PRDVersionRepository) Service {
	return &service{
		repo:        repo,
		versionRepo: versionRepo,
	}
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

	// 记录是否有内容变更
	contentChanged := false
	changeLog := ""

	// 更新字段
	if req.AppVersionID != nil {
		doc.AppVersionID = *req.AppVersionID
	}
	if req.Title != nil && *req.Title != doc.Title {
		changeLog += "标题已更新; "
		doc.Title = *req.Title
		contentChanged = true
	}
	if req.ModuleID != nil {
		doc.ModuleID = req.ModuleID
	}
	if req.Content != nil && *req.Content != doc.Content {
		changeLog += "内容已更新; "
		doc.Content = *req.Content
		contentChanged = true
	}
	if req.Status != nil {
		doc.Status = *req.Status
	}
	if req.Author != nil {
		doc.Author = *req.Author
	}

	// 如果内容有变更，版本号加 1 并创建版本记录
	if contentChanged {
		doc.Version++
		doc.SyncedToVector = false

		// 先更新文档
		if err := s.repo.Update(doc); err != nil {
			return nil, err
		}

		// 创建版本记录
		author := doc.Author
		if req.Author != nil {
			author = *req.Author
		}
		if err := s.createVersion(doc, changeLog, author); err != nil {
			// 版本记录创建失败不影响主流程，只记录错误
			// 实际生产环境可以考虑使用事务
		}
	} else {
		// 没有内容变更，只更新文档
		if err := s.repo.Update(doc); err != nil {
			return nil, err
		}
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


// VersionCompareResponse 版本对比响应
type VersionCompareResponse struct {
	Version1 *prd.PRDVersion `json:"version1"`
	Version2 *prd.PRDVersion `json:"version2"`
	Changes  *VersionChanges `json:"changes"`
}

// VersionChanges 版本变更内容
type VersionChanges struct {
	TitleChanged   bool   `json:"title_changed"`
	ContentChanged bool   `json:"content_changed"`
	OldTitle       string `json:"old_title,omitempty"`
	NewTitle       string `json:"new_title,omitempty"`
}

// createVersion 创建版本记录（内部方法）
func (s *service) createVersion(doc *prd.PRDDocument, changeLog string, createdBy string) error {
	version := &prd.PRDVersion{
		ID:        uuid.New().String(),
		PRDID:     doc.ID,
		Version:   doc.Version,
		Title:     doc.Title,
		Content:   doc.Content,
		ChangeLog: changeLog,
		CreatedBy: createdBy,
		CreatedAt: time.Now(),
	}

	return s.versionRepo.Create(version)
}

// GetPRDVersions 获取 PRD 版本列表
func (s *service) GetPRDVersions(prdID string) ([]*prd.PRDVersion, error) {
	// 检查 PRD 是否存在
	_, err := s.repo.GetByID(prdID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	return s.versionRepo.GetByPRDID(prdID)
}

// GetPRDVersion 获取 PRD 特定版本
func (s *service) GetPRDVersion(prdID string, version int) (*prd.PRDVersion, error) {
	// 检查 PRD 是否存在
	_, err := s.repo.GetByID(prdID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	v, err := s.versionRepo.GetByVersion(prdID, version)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("version not found")
		}
		return nil, err
	}

	return v, nil
}

// ComparePRDVersions 对比两个版本
func (s *service) ComparePRDVersions(prdID string, version1, version2 int) (*VersionCompareResponse, error) {
	// 获取两个版本
	v1, err := s.versionRepo.GetByVersion(prdID, version1)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("version1 not found")
		}
		return nil, err
	}

	v2, err := s.versionRepo.GetByVersion(prdID, version2)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("version2 not found")
		}
		return nil, err
	}

	// 对比变更
	changes := &VersionChanges{
		TitleChanged:   v1.Title != v2.Title,
		ContentChanged: v1.Content != v2.Content,
	}

	if changes.TitleChanged {
		changes.OldTitle = v1.Title
		changes.NewTitle = v2.Title
	}

	return &VersionCompareResponse{
		Version1: v1,
		Version2: v2,
		Changes:  changes,
	}, nil
}


// UpdatePRDStatus 更新 PRD 状态
func (s *service) UpdatePRDStatus(id string, status string) (*prd.PRDDocument, error) {
	// 验证状态值
	validStatuses := map[string]bool{
		"draft":     true,
		"published": true,
		"archived":  true,
	}
	if !validStatuses[status] {
		return nil, errors.New("invalid status, must be one of: draft, published, archived")
	}

	doc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	// 更新状态
	doc.Status = status
	if err := s.repo.Update(doc); err != nil {
		return nil, err
	}

	return s.repo.GetByID(doc.ID)
}

// PublishPRD 发布 PRD
func (s *service) PublishPRD(id string) (*prd.PRDDocument, error) {
	doc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	// 只有草稿状态才能发布
	if doc.Status != "draft" {
		return nil, errors.New("only draft PRD can be published")
	}

	// 更新状态为已发布
	doc.Status = "published"
	if err := s.repo.Update(doc); err != nil {
		return nil, err
	}

	return s.repo.GetByID(doc.ID)
}

// ArchivePRD 归档 PRD
func (s *service) ArchivePRD(id string) (*prd.PRDDocument, error) {
	doc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("PRD not found")
		}
		return nil, err
	}

	// 只有已发布状态才能归档
	if doc.Status != "published" {
		return nil, errors.New("only published PRD can be archived")
	}

	// 更新状态为已归档
	doc.Status = "archived"
	if err := s.repo.Update(doc); err != nil {
		return nil, err
	}

	return s.repo.GetByID(doc.ID)
}
