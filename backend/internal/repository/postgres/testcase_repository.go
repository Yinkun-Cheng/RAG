package postgres

import (
	"rag-backend/internal/domain/testcase"

	"gorm.io/gorm"
)

// TestCaseRepository 测试用例仓储接口
type TestCaseRepository interface {
	Create(tc *testcase.TestCase) error
	GetByID(id string) (*testcase.TestCase, error)
	List(params *TestCaseListParams) ([]*testcase.TestCase, int64, error)
	Update(tc *testcase.TestCase) error
	Delete(id string) error
	GetByCode(projectID, code string) (*testcase.TestCase, error)
	AddTag(testCaseID, tagID string) error
	RemoveTag(testCaseID, tagID string) error
	HasTag(testCaseID, tagID string) (bool, error)
	BatchDelete(ids []string) error
}

// TestCaseListParams 测试用例列表查询参数
type TestCaseListParams struct {
	ProjectID    string
	PRDID        *string
	ModuleID     *string
	Priority     *string
	Type         *string
	Status       *string
	AppVersionID *string
	TagIDs       []string
	Keyword      *string
	Page         int
	PageSize     int
}

type testCaseRepository struct {
	db *gorm.DB
}

// NewTestCaseRepository 创建测试用例仓储实例
func NewTestCaseRepository(db *gorm.DB) TestCaseRepository {
	return &testCaseRepository{db: db}
}

// Create 创建测试用例
func (r *testCaseRepository) Create(tc *testcase.TestCase) error {
	return r.db.Create(tc).Error
}

// GetByID 根据 ID 获取测试用例
func (r *testCaseRepository) GetByID(id string) (*testcase.TestCase, error) {
	var tc testcase.TestCase
	err := r.db.Preload("Module").
		Preload("AppVersion").
		Preload("PRD").
		Preload("Tags").
		Preload("Steps", func(db *gorm.DB) *gorm.DB {
			return db.Order("step_order ASC")
		}).
		Where("id = ?", id).
		First(&tc).Error
	return &tc, err
}

// List 获取测试用例列表（支持分页和筛选）
func (r *testCaseRepository) List(params *TestCaseListParams) ([]*testcase.TestCase, int64, error) {
	var cases []*testcase.TestCase
	var total int64

	query := r.db.Model(&testcase.TestCase{}).
		Where("project_id = ?", params.ProjectID)

	// 按 PRD 筛选
	if params.PRDID != nil && *params.PRDID != "" {
		query = query.Where("prd_id = ?", *params.PRDID)
	}

	// 按模块筛选
	if params.ModuleID != nil && *params.ModuleID != "" {
		query = query.Where("module_id = ?", *params.ModuleID)
	}

	// 按优先级筛选
	if params.Priority != nil && *params.Priority != "" {
		query = query.Where("priority = ?", *params.Priority)
	}

	// 按类型筛选
	if params.Type != nil && *params.Type != "" {
		query = query.Where("type = ?", *params.Type)
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
		query = query.Joins("JOIN test_case_tags ON test_case_tags.test_case_id = test_cases.id").
			Where("test_case_tags.tag_id IN ?", params.TagIDs).
			Group("test_cases.id")
	}

	// 关键词搜索（标题、编号、前置条件、预期结果）
	if params.Keyword != nil && *params.Keyword != "" {
		keyword := "%" + *params.Keyword + "%"
		query = query.Where("title LIKE ? OR code LIKE ? OR precondition LIKE ? OR expected_result LIKE ?", 
			keyword, keyword, keyword, keyword)
	}

	// 统计总数
	if err := query.Count(&total).Error; err != nil {
		return nil, 0, err
	}

	// 分页查询
	offset := (params.Page - 1) * params.PageSize
	err := query.Preload("Module").
		Preload("AppVersion").
		Preload("PRD").
		Preload("Tags").
		Order("created_at DESC").
		Limit(params.PageSize).
		Offset(offset).
		Find(&cases).Error

	return cases, total, err
}

// Update 更新测试用例
func (r *testCaseRepository) Update(tc *testcase.TestCase) error {
	return r.db.Save(tc).Error
}

// Delete 删除测试用例（软删除）
func (r *testCaseRepository) Delete(id string) error {
	return r.db.Where("id = ?", id).Delete(&testcase.TestCase{}).Error
}

// GetByCode 根据编号获取测试用例
func (r *testCaseRepository) GetByCode(projectID, code string) (*testcase.TestCase, error) {
	var tc testcase.TestCase
	err := r.db.Where("project_id = ? AND code = ?", projectID, code).First(&tc).Error
	return &tc, err
}

// AddTag 为测试用例添加标签
func (r *testCaseRepository) AddTag(testCaseID, tagID string) error {
	return r.db.Exec("INSERT INTO test_case_tags (test_case_id, tag_id) VALUES (?, ?)", testCaseID, tagID).Error
}

// RemoveTag 移除测试用例的标签
func (r *testCaseRepository) RemoveTag(testCaseID, tagID string) error {
	return r.db.Exec("DELETE FROM test_case_tags WHERE test_case_id = ? AND tag_id = ?", testCaseID, tagID).Error
}

// HasTag 检查测试用例是否已关联某个标签
func (r *testCaseRepository) HasTag(testCaseID, tagID string) (bool, error) {
	var count int64
	err := r.db.Raw("SELECT COUNT(*) FROM test_case_tags WHERE test_case_id = ? AND tag_id = ?", testCaseID, tagID).Scan(&count).Error
	return count > 0, err
}

// BatchDelete 批量删除测试用例
func (r *testCaseRepository) BatchDelete(ids []string) error {
	return r.db.Where("id IN ?", ids).Delete(&testcase.TestCase{}).Error
}
