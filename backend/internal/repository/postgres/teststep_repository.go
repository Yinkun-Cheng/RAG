package postgres

import (
	"rag-backend/internal/domain/testcase"

	"gorm.io/gorm"
)

// TestStepRepository 测试步骤仓储接口
type TestStepRepository interface {
	CreateBatch(steps []*testcase.TestStep) error
	GetByTestCaseID(testCaseID string) ([]*testcase.TestStep, error)
	UpdateBatch(steps []*testcase.TestStep) error
	DeleteByTestCaseID(testCaseID string) error
}

type testStepRepository struct {
	db *gorm.DB
}

// NewTestStepRepository 创建测试步骤仓储实例
func NewTestStepRepository(db *gorm.DB) TestStepRepository {
	return &testStepRepository{db: db}
}

// CreateBatch 批量创建测试步骤
func (r *testStepRepository) CreateBatch(steps []*testcase.TestStep) error {
	if len(steps) == 0 {
		return nil
	}
	return r.db.Create(&steps).Error
}

// GetByTestCaseID 根据测试用例 ID 获取所有步骤
func (r *testStepRepository) GetByTestCaseID(testCaseID string) ([]*testcase.TestStep, error) {
	var steps []*testcase.TestStep
	err := r.db.Where("test_case_id = ?", testCaseID).
		Order("step_order ASC").
		Find(&steps).Error
	return steps, err
}

// UpdateBatch 批量更新测试步骤（先删除旧的，再创建新的）
func (r *testStepRepository) UpdateBatch(steps []*testcase.TestStep) error {
	if len(steps) == 0 {
		return nil
	}
	
	// 先删除该测试用例的所有步骤
	testCaseID := steps[0].TestCaseID
	if err := r.DeleteByTestCaseID(testCaseID); err != nil {
		return err
	}
	
	// 再创建新的步骤
	return r.CreateBatch(steps)
}

// DeleteByTestCaseID 删除测试用例的所有步骤
func (r *testStepRepository) DeleteByTestCaseID(testCaseID string) error {
	return r.db.Where("test_case_id = ?", testCaseID).Delete(&testcase.TestStep{}).Error
}
