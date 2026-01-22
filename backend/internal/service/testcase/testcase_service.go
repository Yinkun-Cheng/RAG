package testcase

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"time"

	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/testcase"
	"rag-backend/internal/repository/postgres"
	weaviateRepo "rag-backend/internal/repository/weaviate"

	"github.com/google/uuid"
	"gorm.io/gorm"
)

// Service 测试用例服务接口
type Service interface {
	CreateTestCase(projectID string, req *CreateTestCaseRequest) (*testcase.TestCase, error)
	GetTestCase(id string) (*testcase.TestCase, error)
	ListTestCases(projectID string, req *ListTestCaseRequest) (*ListTestCaseResponse, error)
	UpdateTestCase(id string, req *UpdateTestCaseRequest) (*testcase.TestCase, error)
	DeleteTestCase(id string) error
	BatchDeleteTestCases(ids []string) error
	AddTestCaseTag(testCaseID, tagID string) error
	RemoveTestCaseTag(testCaseID, tagID string) error
	GetTestCaseVersions(testCaseID string) ([]*testcase.TestCaseVersion, error)
	GetTestCaseVersion(testCaseID string, version int) (*testcase.TestCaseVersion, error)
}

type service struct {
	repo        postgres.TestCaseRepository
	stepRepo    postgres.TestStepRepository
	versionRepo postgres.TestCaseVersionRepository
	vectorRepo  weaviateRepo.VectorRepository
}

// NewService 创建测试用例服务实例
func NewService(repo postgres.TestCaseRepository, stepRepo postgres.TestStepRepository, versionRepo postgres.TestCaseVersionRepository, vectorRepo weaviateRepo.VectorRepository) Service {
	return &service{
		repo:        repo,
		stepRepo:    stepRepo,
		versionRepo: versionRepo,
		vectorRepo:  vectorRepo,
	}
}

// TestStepRequest 测试步骤请求
type TestStepRequest struct {
	StepOrder   int     `json:"step_order" binding:"required,min=1"`
	Description string  `json:"description" binding:"required"`
	TestData    *string `json:"test_data"`
	Expected    *string `json:"expected"`
}

// CreateTestCaseRequest 创建测试用例请求
type CreateTestCaseRequest struct {
	AppVersionID   string             `json:"app_version_id" binding:"required"`
	Code           string             `json:"code" binding:"required,max=50"`
	Title          string             `json:"title" binding:"required,max=200"`
	PRDID          *string            `json:"prd_id"`
	ModuleID       *string            `json:"module_id"`
	Precondition   string             `json:"precondition"`
	ExpectedResult string             `json:"expected_result" binding:"required"`
	Priority       string             `json:"priority" binding:"required,oneof=P0 P1 P2 P3"`
	Type           string             `json:"type" binding:"required,oneof=functional performance security ui"`
	Steps          []TestStepRequest  `json:"steps"`
}

// UpdateTestCaseRequest 更新测试用例请求
type UpdateTestCaseRequest struct {
	AppVersionID   *string            `json:"app_version_id"`
	Title          *string            `json:"title" binding:"omitempty,max=200"`
	PRDID          *string            `json:"prd_id"`
	ModuleID       *string            `json:"module_id"`
	Precondition   *string            `json:"precondition"`
	ExpectedResult *string            `json:"expected_result"`
	Priority       *string            `json:"priority" binding:"omitempty,oneof=P0 P1 P2 P3"`
	Type           *string            `json:"type" binding:"omitempty,oneof=functional performance security ui"`
	Status         *string            `json:"status" binding:"omitempty,oneof=active deprecated"`
	Steps          *[]TestStepRequest `json:"steps"`
}

// ListTestCaseRequest 获取测试用例列表请求
type ListTestCaseRequest struct {
	PRDID        *string  `form:"prd_id"`
	ModuleID     *string  `form:"module_id"`
	Priority     *string  `form:"priority"`
	Type         *string  `form:"type"`
	Status       *string  `form:"status"`
	AppVersionID *string  `form:"app_version_id"`
	TagIDs       []string `form:"tag_ids"`
	Keyword      *string  `form:"keyword"`
	Page         int      `form:"page" binding:"required,min=1"`
	PageSize     int      `form:"page_size" binding:"required,min=1,max=100"`
}

// ListTestCaseResponse 获取测试用例列表响应
type ListTestCaseResponse struct {
	Items      []*testcase.TestCase `json:"items"`
	Total      int64                `json:"total"`
	Page       int                  `json:"page"`
	PageSize   int                  `json:"page_size"`
	TotalPages int                  `json:"total_pages"`
}

// CreateTestCase 创建测试用例
func (s *service) CreateTestCase(projectID string, req *CreateTestCaseRequest) (*testcase.TestCase, error) {
	// 检查编号是否已存在
	existing, err := s.repo.GetByCode(projectID, req.Code)
	if err == nil && existing != nil {
		return nil, errors.New("test case code already exists")
	}
	if err != nil && !errors.Is(err, gorm.ErrRecordNotFound) {
		return nil, err
	}

	now := time.Now()
	tc := &testcase.TestCase{
		BaseModel: common.BaseModel{
			ID: uuid.New().String(),
		},
		ProjectID:      projectID,
		AppVersionID:   req.AppVersionID,
		Code:           req.Code,
		Title:          req.Title,
		PRDID:          req.PRDID,
		ModuleID:       req.ModuleID,
		Precondition:   req.Precondition,
		ExpectedResult: req.ExpectedResult,
		Priority:       req.Priority,
		Type:           req.Type,
		Status:         "active",
		Version:        1,
		SyncedToVector: false,
		SyncStatus:     nil,
		LastSyncedAt:   &now,
	}

	// 创建测试用例
	if err := s.repo.Create(tc); err != nil {
		return nil, err
	}

	// 异步同步到 Weaviate
	go s.syncTestCaseToVector(tc)

	// 创建测试步骤
	if len(req.Steps) > 0 {
		steps := make([]*testcase.TestStep, len(req.Steps))
		for i, stepReq := range req.Steps {
			steps[i] = &testcase.TestStep{
				ID:          uuid.New().String(),
				TestCaseID:  tc.ID,
				StepOrder:   stepReq.StepOrder,
				Description: stepReq.Description,
				TestData:    stepReq.TestData,
				Expected:    stepReq.Expected,
			}
		}
		if err := s.stepRepo.CreateBatch(steps); err != nil {
			return nil, err
		}
	}

	// 重新查询以获取关联数据
	return s.repo.GetByID(tc.ID)
}

// GetTestCase 获取测试用例详情
func (s *service) GetTestCase(id string) (*testcase.TestCase, error) {
	tc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("test case not found")
		}
		return nil, err
	}
	return tc, nil
}

// ListTestCases 获取测试用例列表
func (s *service) ListTestCases(projectID string, req *ListTestCaseRequest) (*ListTestCaseResponse, error) {
	params := &postgres.TestCaseListParams{
		ProjectID:    projectID,
		PRDID:        req.PRDID,
		ModuleID:     req.ModuleID,
		Priority:     req.Priority,
		Type:         req.Type,
		Status:       req.Status,
		AppVersionID: req.AppVersionID,
		TagIDs:       req.TagIDs,
		Keyword:      req.Keyword,
		Page:         req.Page,
		PageSize:     req.PageSize,
	}

	cases, total, err := s.repo.List(params)
	if err != nil {
		return nil, err
	}

	totalPages := int(total) / req.PageSize
	if int(total)%req.PageSize > 0 {
		totalPages++
	}

	return &ListTestCaseResponse{
		Items:      cases,
		Total:      total,
		Page:       req.Page,
		PageSize:   req.PageSize,
		TotalPages: totalPages,
	}, nil
}

// UpdateTestCase 更新测试用例
func (s *service) UpdateTestCase(id string, req *UpdateTestCaseRequest) (*testcase.TestCase, error) {
	tc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("test case not found")
		}
		return nil, err
	}

	// 记录是否有内容变更
	contentChanged := false
	changeLog := ""

	// 更新字段
	if req.AppVersionID != nil {
		tc.AppVersionID = *req.AppVersionID
	}
	if req.Title != nil && *req.Title != tc.Title {
		changeLog += "标题已更新; "
		tc.Title = *req.Title
		contentChanged = true
	}
	if req.PRDID != nil {
		tc.PRDID = req.PRDID
	}
	if req.ModuleID != nil {
		tc.ModuleID = req.ModuleID
	}
	if req.Precondition != nil && *req.Precondition != tc.Precondition {
		changeLog += "前置条件已更新; "
		tc.Precondition = *req.Precondition
		contentChanged = true
	}
	if req.ExpectedResult != nil && *req.ExpectedResult != tc.ExpectedResult {
		changeLog += "预期结果已更新; "
		tc.ExpectedResult = *req.ExpectedResult
		contentChanged = true
	}
	if req.Priority != nil {
		tc.Priority = *req.Priority
	}
	if req.Type != nil {
		tc.Type = *req.Type
	}
	if req.Status != nil {
		tc.Status = *req.Status
	}

	// 更新测试步骤
	// 只要 req.Steps 不为 nil，就表示前端想要更新步骤（即使是空数组）
	if req.Steps != nil {
		// 先删除旧步骤
		if err := s.stepRepo.DeleteByTestCaseID(tc.ID); err != nil {
			return nil, err
		}
		
		// 清空 tc.Steps，避免 GORM 的 Save 方法自动保存旧步骤
		tc.Steps = nil
		
		// 如果有新步骤，则创建
		if len(*req.Steps) > 0 {
			steps := make([]*testcase.TestStep, len(*req.Steps))
			for i, stepReq := range *req.Steps {
				steps[i] = &testcase.TestStep{
					ID:          uuid.New().String(),
					TestCaseID:  tc.ID,
					StepOrder:   stepReq.StepOrder,
					Description: stepReq.Description,
					TestData:    stepReq.TestData,
					Expected:    stepReq.Expected,
				}
			}
			if err := s.stepRepo.CreateBatch(steps); err != nil {
				return nil, err
			}
		}
		changeLog += "测试步骤已更新; "
		contentChanged = true
	}

	// 如果内容有变更，版本号加 1 并创建版本记录
	if contentChanged {
		tc.Version++
		tc.SyncedToVector = false

		// 先更新测试用例
		if err := s.repo.Update(tc); err != nil {
			return nil, err
		}

		// 异步同步到 Weaviate
		go s.syncTestCaseToVector(tc)

		// 创建版本记录
		createdBy := "system"
		if err := s.createVersion(tc, changeLog, createdBy); err != nil {
			// 版本记录创建失败不影响主流程，只记录错误
		}
	} else {
		// 没有内容变更，只更新测试用例
		if err := s.repo.Update(tc); err != nil {
			return nil, err
		}
	}

	// 重新查询以获取关联数据
	return s.repo.GetByID(tc.ID)
}

// DeleteTestCase 删除测试用例
func (s *service) DeleteTestCase(id string) error {
	// 检查是否存在
	tc, err := s.repo.GetByID(id)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("test case not found")
		}
		return err
	}

	// 从 PostgreSQL 删除
	if err := s.repo.Delete(id); err != nil {
		return err
	}

	// 异步从 Weaviate 删除
	go s.deleteTestCaseFromVector(tc.ID)

	return nil
}

// BatchDeleteTestCases 批量删除测试用例
func (s *service) BatchDeleteTestCases(ids []string) error {
	if len(ids) == 0 {
		return errors.New("no test case IDs provided")
	}
	return s.repo.BatchDelete(ids)
}

// AddTestCaseTag 为测试用例添加标签
func (s *service) AddTestCaseTag(testCaseID, tagID string) error {
	// 检查测试用例是否存在
	_, err := s.repo.GetByID(testCaseID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("test case not found")
		}
		return err
	}

	// 检查是否已经关联
	hasTag, err := s.repo.HasTag(testCaseID, tagID)
	if err != nil {
		return err
	}
	if hasTag {
		return errors.New("tag already associated with this test case")
	}

	// 添加标签关联
	return s.repo.AddTag(testCaseID, tagID)
}

// RemoveTestCaseTag 移除测试用例的标签
func (s *service) RemoveTestCaseTag(testCaseID, tagID string) error {
	// 检查测试用例是否存在
	_, err := s.repo.GetByID(testCaseID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return errors.New("test case not found")
		}
		return err
	}

	// 检查是否已关联
	hasTag, err := s.repo.HasTag(testCaseID, tagID)
	if err != nil {
		return err
	}
	if !hasTag {
		return errors.New("tag not associated with this test case")
	}

	// 移除标签关联
	return s.repo.RemoveTag(testCaseID, tagID)
}


// createVersion 创建版本记录（内部方法）
func (s *service) createVersion(tc *testcase.TestCase, changeLog string, createdBy string) error {
	// 获取测试步骤
	steps, err := s.stepRepo.GetByTestCaseID(tc.ID)
	if err != nil {
		return err
	}

	// 构建快照（包含测试步骤）
	snapshot := map[string]interface{}{
		"title":           tc.Title,
		"precondition":    tc.Precondition,
		"expected_result": tc.ExpectedResult,
		"priority":        tc.Priority,
		"type":            tc.Type,
		"steps":           steps,
	}

	// 将快照转换为 JSON
	snapshotJSON, err := json.Marshal(snapshot)
	if err != nil {
		return err
	}

	version := &testcase.TestCaseVersion{
		ID:             uuid.New().String(),
		TestCaseID:     tc.ID,
		Version:        tc.Version,
		Title:          tc.Title,
		Precondition:   tc.Precondition,
		ExpectedResult: tc.ExpectedResult,
		Priority:       tc.Priority,
		Type:           tc.Type,
		ChangeLog:      changeLog,
		Snapshot:       snapshotJSON,
		CreatedBy:      createdBy,
		CreatedAt:      time.Now(),
	}

	return s.versionRepo.Create(version)
}

// GetTestCaseVersions 获取测试用例版本列表
func (s *service) GetTestCaseVersions(testCaseID string) ([]*testcase.TestCaseVersion, error) {
	// 检查测试用例是否存在
	_, err := s.repo.GetByID(testCaseID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("test case not found")
		}
		return nil, err
	}

	return s.versionRepo.GetByTestCaseID(testCaseID)
}

// GetTestCaseVersion 获取测试用例特定版本
func (s *service) GetTestCaseVersion(testCaseID string, version int) (*testcase.TestCaseVersion, error) {
	// 检查测试用例是否存在
	_, err := s.repo.GetByID(testCaseID)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("test case not found")
		}
		return nil, err
	}

	v, err := s.versionRepo.GetByVersion(testCaseID, version)
	if err != nil {
		if errors.Is(err, gorm.ErrRecordNotFound) {
			return nil, errors.New("version not found")
		}
		return nil, err
	}

	return v, nil
}

// syncTestCaseToVector 异步同步测试用例到 Weaviate
func (s *service) syncTestCaseToVector(tc *testcase.TestCase) {
	ctx := context.Background()

	err := s.vectorRepo.SyncTestCase(
		ctx,
		tc.ID,
		tc.ProjectID,
		tc.ModuleID,
		tc.PRDID,
		tc.Title,
		tc.Priority,
		tc.Type,
		tc.Status,
		tc.CreatedAt,
	)

	if err != nil {
		// 同步失败，更新同步状态
		syncStatus := err.Error()
		tc.SyncedToVector = false
		tc.SyncStatus = &syncStatus
		s.repo.Update(tc)
	} else {
		// 同步成功，更新同步状态
		now := time.Now()
		tc.SyncedToVector = true
		tc.SyncStatus = nil
		tc.LastSyncedAt = &now
		s.repo.Update(tc)
	}
}

// deleteTestCaseFromVector 异步从 Weaviate 删除测试用例
func (s *service) deleteTestCaseFromVector(testCaseID string) {
	ctx := context.Background()
	_ = s.vectorRepo.DeleteTestCase(ctx, testCaseID)
}
