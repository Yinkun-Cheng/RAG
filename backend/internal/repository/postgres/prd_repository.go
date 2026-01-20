package postgres

import (
	"rag-backend/internal/domain/prd"

	"gorm.io/gorm"
)

// PRDRepository PRD 文档仓储接口
type PRDRepository interface {
	Create(doc *prd.PRDDocument) error
	GetByID(id string) (*prd.PRDDocument, error)
	List(params *PRDListParams) ([]*prd.PRDDocument, int64, error)
	Update(doc *prd.PRDDocument) error
	Delete(id string) error
	GetByCode(projectID, code string) (*prd.PRDDocument, error)
	AddTag(prdID, tagID string) error
	RemoveTag(prdID, tagID string) error
	HasTag(prdID, tagID string) (bool, error)
}

// PRDListParams PRD 列表查询参数
type PRDListParams struct {
	ProjectID    string
	ModuleID     *string
	Status       *string
	AppVersionID *string
	TagIDs       []string
	Keyword      *string
	Page         int
	PageSize     int
}

type prdRepository struct {
	db *gorm.DB
}

// NewPRDRepository 创建 PRD 文档仓储实例
func NewPRDRepository(db *gorm.DB) PRDRepository {
	return &prdRepository{db: db}
}

// Create 创建 PRD 文档
func (r *prdRepository) Create(doc *prd.PRDDocument) error {
	return r.db.Create(doc).Error
}

// GetByID 根据 ID 获取 PRD 文档
func (r *prdRepository) GetByID(id string) (*prd.PRDDocument, error) {
	var doc prd.PRDDocument
	err := r.db.Preload("Module").
		Preload("AppVersion").
		Preload("Tags").
		Where("id = ?", id).
		First(&doc).Error
	return &doc, err
}

// List 获取 PRD 文档列表（支持分页和筛选）
func (r *prdRepository) List(params *PRDListParams) ([]*prd.PRDDocument, int64, error) {
	var docs []*prd.PRDDocument
	var total int64

	query := r.db.Model(&prd.PRDDocument{}).
		Where("project_id = ?", params.ProjectID)

	// 按模块筛选
	if params.ModuleID != nil && *params.ModuleID != "" {
		query = query.Where("module_id = ?", *params.ModuleID)
	}

	// 按状态筛选
	if params.Status != nil && *params.Status != "" {
		query = query.Where("status = ?", *params.Status)
	}

	// 按 App 版本筛选
	if params.AppVersionID != nil && *params.AppVersionID != "" {
		query = query.Where("app_version_id = ?", *params.AppVersionID)
	}

	// 按标签筛选
	if len(params.TagIDs) > 0 {
		query = query.Joins("JOIN prd_tags ON prd_tags.prd_id = prd_documents.id").
			Where("prd_tags.tag_id IN ?", params.TagIDs).
			Group("prd_documents.id")
	}

	// 关键词搜索（标题和内容）
	if params.Keyword != nil && *params.Keyword != "" {
		keyword := "%" + *params.Keyword + "%"
		query = query.Where("title LIKE ? OR content LIKE ? OR code LIKE ?", keyword, keyword, keyword)
	}

	// 统计总数
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 分页查询
	offset := (params.Page - 1) * params.PageSize
	err := query.Preload("Module").
		Preload("AppVersion").
		Preload("Tags").
		Order("created_at DESC").
		Limit(params.PageSize).
		Offset(offset).
		Find(&docs).Error

	return docs, total, err
}

// Update 更新 PRD 文档
func (r *prdRepository) Update(doc *prd.PRDDocument) error {
	return r.db.Save(doc).Error
}

// Delete 删除 PRD 文档（软删除）
func (r *prdRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&prd.PRDDocument{}).Error
}

// GetByCode 根据编号获取 PRD 文档
func (r *prdRepository) GetByCode(projectID, code string) (*prd.PRDDocument, error) {
	var doc prd.PRDDocument
	err := r.db.Where("project_id = ? AND code = ?", projectID, code).First(&doc).Error
	return &doc, err
}

// AddTag 为 PRD 添加标签
func (r *prdRepository) AddTag(prdID, tagID string) error {
	// 使用原生 SQL 插入关联记录
	return r.db.Exec("INSERT INTO prd_tags (prd_id, tag_id) VALUES (?, ?)", prdID, tagID).Error
}

// RemoveTag 移除 PRD 的标签
func (r *prdRepository) RemoveTag(prdID, tagID string) error {
	return r.db.Exec("DELETE FROM prd_tags WHERE prd_id = ? AND tag_id = ?", prdID, tagID).Error
}

// HasTag 检查 PRD 是否已关联某个标签
func (r *prdRepository) HasTag(prdID, tagID string) (bool, error) {
	var count int64
	err := r.db.Raw("SELECT COUNT(*) FROM prd_tags WHERE prd_id = ? AND tag_id = ?", prdID, tagID).Scan(&count).Error
	return count > 0, err
}
