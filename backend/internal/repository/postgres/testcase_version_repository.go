package postgres

import (
	"rag-backend/internal/domain/testcase"

	"gorm.io/gorm"
)

// TestCaseVersionRepository 测试用例版本仓储接口
type TestCaseVersionRepository interface {
	Create(version *testcase.TestCaseVersion) error
	GetByTestCaseID(testCaseID string) ([]*testcase.TestCaseVersion, error)
	GetByVersion(testCaseID string, version int) (*testcase.TestCaseVersion, error)
}

type testCaseVersionRepository struct {
	db *gorm.DB
}

// NewTestCaseVersionRepository 创建测试用例版本仓储实例
func NewTestCaseVersionRepository(db *gorm.DB) TestCaseVersionRepository {
	return &testCaseVersionRepository{db: db}
}

// Create 创建测试用例版本记录
func (r *testCaseVersionRepository) Create(version *testcase.TestCaseVersion) error {
	return r.db.Create(version).Error
}

// GetByTestCaseID 根据测试用例 ID 获取所有版本
func (r *testCaseVersionRepository) GetByTestCaseID(testCaseID string) ([]*testcase.TestCaseVersion, error) {
	var versions []*testcase.TestCaseVersion
	err := r.db.Where("test_case_id = ?", testCaseID).
		Order("version DESC").
		Find(&versions).Error
	return versions, err
}

// GetByVersion 根据测试用例 ID 和版本号获取特定版本
func (r *testCaseVersionRepository) GetByVersion(testCaseID string, version int) (*testcase.TestCaseVersion, error) {
	var v testcase.TestCaseVersion
	err := r.db.Where("test_case_id = ? AND version = ?", testCaseID, version).
		First(&v).Error
	return &v, err
}
