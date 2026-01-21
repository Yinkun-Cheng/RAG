package statistics

import (
	"errors"

	"gorm.io/gorm"
)

// Service 统计服务接口
type Service interface {
	GetProjectStatistics(projectID string) (*ProjectStatistics, error)
	GetTrends(projectID string, days int) (*TrendsResponse, error)
	GetCoverage(projectID string) (*CoverageResponse, error)
}

type service struct {
	db *gorm.DB
}

// NewService 创建统计服务实例
func NewService(db *gorm.DB) Service {
	return &service{db: db}
}

// ProjectStatistics 项目统计信息
type ProjectStatistics struct {
	// 总数统计
	TotalPRDs      int64 `json:"total_prds"`
	TotalTestCases int64 `json:"total_test_cases"`
	TotalModules   int64 `json:"total_modules"`
	TotalTags      int64 `json:"total_tags"`

	// PRD 状态统计
	PRDByStatus map[string]int64 `json:"prd_by_status"`

	// 测试用例优先级统计
	TestCasesByPriority map[string]int64 `json:"test_cases_by_priority"`

	// 测试用例类型统计
	TestCasesByType map[string]int64 `json:"test_cases_by_type"`

	// 测试用例状态统计
	TestCasesByStatus map[string]int64 `json:"test_cases_by_status"`

	// 按模块统计
	ByModule []ModuleStatistics `json:"by_module"`
}

// ModuleStatistics 模块统计信息
type ModuleStatistics struct {
	ModuleID       string `json:"module_id"`
	ModuleName     string `json:"module_name"`
	PRDCount       int64  `json:"prd_count"`
	TestCaseCount  int64  `json:"test_case_count"`
}

// TrendsResponse 趋势分析响应
type TrendsResponse struct {
	Days      int                  `json:"days"`
	PRDTrend  []DailyCount         `json:"prd_trend"`
	TestCaseTrend []DailyCount      `json:"test_case_trend"`
}

// DailyCount 每日统计
type DailyCount struct {
	Date  string `json:"date"`
	Count int64  `json:"count"`
}

// CoverageResponse 覆盖率统计响应
type CoverageResponse struct {
	TotalPRDs              int64   `json:"total_prds"`
	PRDsWithTestCases      int64   `json:"prds_with_test_cases"`
	PRDsWithoutTestCases   int64   `json:"prds_without_test_cases"`
	CoverageRate           float64 `json:"coverage_rate"`
	ModuleCoverage         []ModuleCoverage `json:"module_coverage"`
}

// ModuleCoverage 模块覆盖率
type ModuleCoverage struct {
	ModuleID             string  `json:"module_id"`
	ModuleName           string  `json:"module_name"`
	TotalPRDs            int64   `json:"total_prds"`
	PRDsWithTestCases    int64   `json:"prds_with_test_cases"`
	CoverageRate         float64 `json:"coverage_rate"`
}

// GetProjectStatistics 获取项目统计信息
func (s *service) GetProjectStatistics(projectID string) (*ProjectStatistics, error) {
	stats := &ProjectStatistics{
		PRDByStatus:         make(map[string]int64),
		TestCasesByPriority: make(map[string]int64),
		TestCasesByType:     make(map[string]int64),
		TestCasesByStatus:   make(map[string]int64),
		ByModule:            []ModuleStatistics{},
	}

	// 检查项目是否存在
	var projectExists int64
	if err := s.db.Table("projects").Where("id = ? AND deleted_at IS NULL", projectID).Count(&projectExists).Error; err != nil {
		return nil, err
	}
	if projectExists == 0 {
		return nil, errors.New("project not found")
	}

	// 统计总数
	if err := s.db.Table("prd_documents").Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&stats.TotalPRDs).Error; err != nil {
		return nil, err
	}

	if err := s.db.Table("test_cases").Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&stats.TotalTestCases).Error; err != nil {
		return nil, err
	}

	if err := s.db.Table("modules").Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&stats.TotalModules).Error; err != nil {
		return nil, err
	}

	if err := s.db.Table("tags").Where("project_id = ? AND deleted_at IS NULL", projectID).Count(&stats.TotalTags).Error; err != nil {
		return nil, err
	}

	// PRD 按状态统计
	var prdStatusResults []struct {
		Status string
		Count  int64
	}
	if err := s.db.Table("prd_documents").
		Select("status, COUNT(*) as count").
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("status").
		Scan(&prdStatusResults).Error; err != nil {
		return nil, err
	}
	for _, r := range prdStatusResults {
		stats.PRDByStatus[r.Status] = r.Count
	}

	// 测试用例按优先级统计
	var priorityResults []struct {
		Priority string
		Count    int64
	}
	if err := s.db.Table("test_cases").
		Select("priority, COUNT(*) as count").
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("priority").
		Scan(&priorityResults).Error; err != nil {
		return nil, err
	}
	for _, r := range priorityResults {
		stats.TestCasesByPriority[r.Priority] = r.Count
	}

	// 测试用例按类型统计
	var typeResults []struct {
		Type  string
		Count int64
	}
	if err := s.db.Table("test_cases").
		Select("type, COUNT(*) as count").
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("type").
		Scan(&typeResults).Error; err != nil {
		return nil, err
	}
	for _, r := range typeResults {
		stats.TestCasesByType[r.Type] = r.Count
	}

	// 测试用例按状态统计
	var statusResults []struct {
		Status string
		Count  int64
	}
	if err := s.db.Table("test_cases").
		Select("status, COUNT(*) as count").
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Group("status").
		Scan(&statusResults).Error; err != nil {
		return nil, err
	}
	for _, r := range statusResults {
		stats.TestCasesByStatus[r.Status] = r.Count
	}

	// 按模块统计
	var moduleResults []struct {
		ModuleID   string
		ModuleName string
		PRDCount   int64
		TestCaseCount int64
	}
	if err := s.db.Raw(`
		SELECT 
			m.id as module_id,
			m.name as module_name,
			COALESCE(prd_counts.count, 0) as prd_count,
			COALESCE(tc_counts.count, 0) as test_case_count
		FROM modules m
		LEFT JOIN (
			SELECT module_id, COUNT(*) as count
			FROM prd_documents
			WHERE project_id = ? AND deleted_at IS NULL AND module_id IS NOT NULL
			GROUP BY module_id
		) prd_counts ON m.id = prd_counts.module_id
		LEFT JOIN (
			SELECT module_id, COUNT(*) as count
			FROM test_cases
			WHERE project_id = ? AND deleted_at IS NULL AND module_id IS NOT NULL
			GROUP BY module_id
		) tc_counts ON m.id = tc_counts.module_id
		WHERE m.project_id = ? AND m.deleted_at IS NULL
		ORDER BY m.sort_order, m.name
	`, projectID, projectID, projectID).Scan(&moduleResults).Error; err != nil {
		return nil, err
	}

	for _, r := range moduleResults {
		stats.ByModule = append(stats.ByModule, ModuleStatistics{
			ModuleID:      r.ModuleID,
			ModuleName:    r.ModuleName,
			PRDCount:      r.PRDCount,
			TestCaseCount: r.TestCaseCount,
		})
	}

	return stats, nil
}

// GetTrends 获取趋势分析
func (s *service) GetTrends(projectID string, days int) (*TrendsResponse, error) {
	if days <= 0 {
		days = 30 // 默认 30 天
	}

	// 检查项目是否存在
	var projectExists int64
	if err := s.db.Table("projects").Where("id = ? AND deleted_at IS NULL", projectID).Count(&projectExists).Error; err != nil {
		return nil, err
	}
	if projectExists == 0 {
		return nil, errors.New("project not found")
	}

	trends := &TrendsResponse{
		Days:          days,
		PRDTrend:      []DailyCount{},
		TestCaseTrend: []DailyCount{},
	}

	// PRD 创建趋势
	var prdTrendResults []struct {
		Date  string
		Count int64
	}
	if err := s.db.Raw(`
		SELECT 
			DATE(created_at) as date,
			COUNT(*) as count
		FROM prd_documents
		WHERE project_id = ? 
			AND deleted_at IS NULL
			AND created_at >= CURRENT_DATE - INTERVAL '1 day' * ?
		GROUP BY DATE(created_at)
		ORDER BY date
	`, projectID, days).Scan(&prdTrendResults).Error; err != nil {
		return nil, err
	}
	for _, r := range prdTrendResults {
		trends.PRDTrend = append(trends.PRDTrend, DailyCount{
			Date:  r.Date,
			Count: r.Count,
		})
	}

	// 测试用例创建趋势
	var tcTrendResults []struct {
		Date  string
		Count int64
	}
	if err := s.db.Raw(`
		SELECT 
			DATE(created_at) as date,
			COUNT(*) as count
		FROM test_cases
		WHERE project_id = ? 
			AND deleted_at IS NULL
			AND created_at >= CURRENT_DATE - INTERVAL '1 day' * ?
		GROUP BY DATE(created_at)
		ORDER BY date
	`, projectID, days).Scan(&tcTrendResults).Error; err != nil {
		return nil, err
	}
	for _, r := range tcTrendResults {
		trends.TestCaseTrend = append(trends.TestCaseTrend, DailyCount{
			Date:  r.Date,
			Count: r.Count,
		})
	}

	return trends, nil
}

// GetCoverage 获取覆盖率统计
func (s *service) GetCoverage(projectID string) (*CoverageResponse, error) {
	// 检查项目是否存在
	var projectExists int64
	if err := s.db.Table("projects").Where("id = ? AND deleted_at IS NULL", projectID).Count(&projectExists).Error; err != nil {
		return nil, err
	}
	if projectExists == 0 {
		return nil, errors.New("project not found")
	}

	coverage := &CoverageResponse{
		ModuleCoverage: []ModuleCoverage{},
	}

	// 统计总 PRD 数量
	if err := s.db.Table("prd_documents").
		Where("project_id = ? AND deleted_at IS NULL", projectID).
		Count(&coverage.TotalPRDs).Error; err != nil {
		return nil, err
	}

	// 统计有测试用例的 PRD 数量
	if err := s.db.Raw(`
		SELECT COUNT(DISTINCT prd_id)
		FROM test_cases
		WHERE project_id = ? AND deleted_at IS NULL AND prd_id IS NOT NULL
	`, projectID).Scan(&coverage.PRDsWithTestCases).Error; err != nil {
		return nil, err
	}

	coverage.PRDsWithoutTestCases = coverage.TotalPRDs - coverage.PRDsWithTestCases

	// 计算覆盖率
	if coverage.TotalPRDs > 0 {
		coverage.CoverageRate = float64(coverage.PRDsWithTestCases) / float64(coverage.TotalPRDs) * 100
	}

	// 按模块统计覆盖率
	// 先获取每个模块的 PRD 总数（使用与项目统计相同的逻辑）
	var moduleResults []struct {
		ModuleID   string
		ModuleName string
		PRDCount   int64
	}
	if err := s.db.Raw(`
		SELECT 
			m.id as module_id,
			m.name as module_name,
			COALESCE(prd_counts.count, 0) as prd_count
		FROM modules m
		LEFT JOIN (
			SELECT module_id, COUNT(*) as count
			FROM prd_documents
			WHERE project_id = ? AND deleted_at IS NULL AND module_id IS NOT NULL
			GROUP BY module_id
		) prd_counts ON m.id = prd_counts.module_id
		WHERE m.project_id = ? AND m.deleted_at IS NULL
		ORDER BY m.sort_order, m.name
	`, projectID, projectID).Scan(&moduleResults).Error; err != nil {
		return nil, err
	}

	// 再获取每个模块有测试用例的 PRD 数量
	var coveredResults []struct {
		ModuleID string
		Count    int64
	}
	if err := s.db.Raw(`
		SELECT p.module_id, COUNT(DISTINCT p.id) as count
		FROM prd_documents p
		INNER JOIN test_cases tc ON tc.prd_id = p.id AND tc.deleted_at IS NULL
		WHERE p.project_id = ? AND p.deleted_at IS NULL AND p.module_id IS NOT NULL
		GROUP BY p.module_id
	`, projectID).Scan(&coveredResults).Error; err != nil {
		return nil, err
	}

	// 构建覆盖率映射
	coveredMap := make(map[string]int64)
	for _, r := range coveredResults {
		coveredMap[r.ModuleID] = r.Count
	}

	// 组合结果
	for _, r := range moduleResults {
		coveredCount := coveredMap[r.ModuleID]
		coverageRate := 0.0
		if r.PRDCount > 0 {
			coverageRate = float64(coveredCount) / float64(r.PRDCount) * 100
		}
		coverage.ModuleCoverage = append(coverage.ModuleCoverage, ModuleCoverage{
			ModuleID:          r.ModuleID,
			ModuleName:        r.ModuleName,
			TotalPRDs:         r.PRDCount,
			PRDsWithTestCases: coveredCount,
			CoverageRate:      coverageRate,
		})
	}

	return coverage, nil
}
