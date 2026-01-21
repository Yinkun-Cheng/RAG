package search

import (
	"context"
	"fmt"
	"strconv"
	"rag-backend/internal/domain/testcase"
	"rag-backend/internal/pkg/weaviate"
	"rag-backend/internal/repository/postgres"

	"gorm.io/gorm"
)

// SearchService 搜索服务
type SearchService struct {
	db               *gorm.DB
	weaviateClient   *weaviate.Client
	embeddingManager *weaviate.EmbeddingManager
	prdRepo          postgres.PRDRepository
	testcaseRepo     postgres.TestCaseRepository
}

// SearchConfig 搜索配置
type SearchConfig struct {
	DefaultAlpha     float32
	DefaultLimit     int
	DefaultThreshold float32
	EnableHybrid     bool
}

// loadSearchConfig 从数据库加载搜索配置
func (s *SearchService) loadSearchConfig(ctx context.Context) (*SearchConfig, error) {
	config := &SearchConfig{
		DefaultAlpha:     1.0,  // 默认纯向量检索
		DefaultLimit:     10,   // 默认返回 10 条
		DefaultThreshold: 0.7,  // 默认相似度阈值 0.7
		EnableHybrid:     true, // 默认启用混合检索
	}

	// 从数据库读取配置
	var settings []struct {
		Key   string
		Value string
	}

	err := s.db.WithContext(ctx).
		Table("global_settings").
		Select("key, value").
		Where("key IN ?", []string{
			"search_default_alpha",
			"search_default_limit",
			"search_default_threshold",
			"search_enable_hybrid",
		}).
		Find(&settings).Error

	if err != nil {
		// 如果读取失败，使用默认值
		return config, nil
	}

	// 解析配置
	for _, setting := range settings {
		switch setting.Key {
		case "search_default_alpha":
			if val, err := strconv.ParseFloat(setting.Value, 32); err == nil {
				config.DefaultAlpha = float32(val)
			}
		case "search_default_limit":
			if val, err := strconv.Atoi(setting.Value); err == nil {
				config.DefaultLimit = val
			}
		case "search_default_threshold":
			if val, err := strconv.ParseFloat(setting.Value, 32); err == nil {
				config.DefaultThreshold = float32(val)
			}
		case "search_enable_hybrid":
			config.EnableHybrid = setting.Value == "true"
		}
	}

	return config, nil
}

// NewSearchService 创建搜索服务实例
func NewSearchService(
	db *gorm.DB,
	weaviateClient *weaviate.Client,
	embeddingManager *weaviate.EmbeddingManager,
) *SearchService {
	return &SearchService{
		db:               db,
		weaviateClient:   weaviateClient,
		embeddingManager: embeddingManager,
		prdRepo:          postgres.NewPRDRepository(db),
		testcaseRepo:     postgres.NewTestCaseRepository(db),
	}
}

// SearchType 搜索类型
type SearchType string

const (
	SearchTypePRD      SearchType = "prd"
	SearchTypeTestCase SearchType = "testcase"
	SearchTypeAll      SearchType = "all"
)

// SearchRequest 搜索请求
type SearchRequest struct {
	Query            string     `json:"query" binding:"required"`              // 搜索查询
	Type             SearchType `json:"type" binding:"required"`               // 搜索类型
	Limit            int        `json:"limit"`                                 // 结果数量限制
	ScoreThreshold   float32    `json:"score_threshold"`                       // 相似度阈值
	ProjectID        string     `json:"project_id"`                            // 项目ID（可选）
	ModuleID         *string    `json:"module_id"`                             // 模块ID（可选）
	AppVersionID     *string    `json:"app_version_id"`                        // App版本ID（可选）
	Status           *string    `json:"status"`                                // 状态（可选）
	IncludeArchived  bool       `json:"include_archived"`                      // 是否包含已归档
	Alpha            *float32   `json:"alpha"`                                 // 混合检索权重（0-1，0=纯BM25，1=纯向量，默认1）
}

// SearchResult 搜索结果
type SearchResult struct {
	Type       SearchType             `json:"type"`        // 结果类型
	ID         string                 `json:"id"`          // 文档ID
	Title      string                 `json:"title"`       // 标题
	Content    string                 `json:"content"`     // 内容摘要
	Score      float32                `json:"score"`       // 相似度分数
	Metadata   map[string]interface{} `json:"metadata"`    // 元数据
	Highlights []string               `json:"highlights"`  // 高亮片段
}

// SearchResponse 搜索响应
type SearchResponse struct {
	Results    []SearchResult `json:"results"`     // 搜索结果
	Total      int            `json:"total"`       // 总数
	Query      string         `json:"query"`       // 查询
	Type       SearchType     `json:"type"`        // 搜索类型
}

// Search 执行语义搜索
func (s *SearchService) Search(ctx context.Context, req *SearchRequest) (*SearchResponse, error) {
	// 加载搜索配置
	config, err := s.loadSearchConfig(ctx)
	if err != nil {
		return nil, fmt.Errorf("加载搜索配置失败: %w", err)
	}

	// 设置默认值（使用配置的默认值）
	if req.Limit <= 0 {
		req.Limit = config.DefaultLimit
	}
	if req.ScoreThreshold <= 0 {
		req.ScoreThreshold = config.DefaultThreshold
	}
	if req.Alpha == nil {
		req.Alpha = &config.DefaultAlpha
	}

	// 如果禁用了混合检索，强制使用纯向量检索
	if !config.EnableHybrid && *req.Alpha < 1.0 {
		pureVector := float32(1.0)
		req.Alpha = &pureVector
	}

	// 生成查询向量
	embeddingService := s.embeddingManager.GetService()
	if embeddingService == nil {
		return nil, fmt.Errorf("Embedding 服务未初始化")
	}
	
	embedding, err := embeddingService.Embed(ctx, req.Query)
	if err != nil {
		return nil, fmt.Errorf("生成查询向量失败: %w", err)
	}

	var results []SearchResult

	// 根据搜索类型执行搜索
	switch req.Type {
	case SearchTypePRD:
		prdResults, err := s.searchPRDs(ctx, embedding, req)
		if err != nil {
			return nil, err
		}
		results = append(results, prdResults...)

	case SearchTypeTestCase:
		testcaseResults, err := s.searchTestCases(ctx, embedding, req)
		if err != nil {
			return nil, err
		}
		results = append(results, testcaseResults...)

	case SearchTypeAll:
		// 搜索 PRD
		prdResults, err := s.searchPRDs(ctx, embedding, req)
		if err != nil {
			return nil, err
		}
		results = append(results, prdResults...)

		// 搜索测试用例
		testcaseResults, err := s.searchTestCases(ctx, embedding, req)
		if err != nil {
			return nil, err
		}
		results = append(results, testcaseResults...)

	default:
		return nil, fmt.Errorf("不支持的搜索类型: %s", req.Type)
	}

	// 按分数排序并限制结果数量
	results = s.sortAndLimitResults(results, req.Limit)

	return &SearchResponse{
		Results: results,
		Total:   len(results),
		Query:   req.Query,
		Type:    req.Type,
	}, nil
}

// searchPRDs 搜索 PRD 文档
func (s *SearchService) searchPRDs(ctx context.Context, embedding []float32, req *SearchRequest) ([]SearchResult, error) {
	// 构建过滤条件
	filters := s.buildPRDFilters(req)

	var weaviateResults []weaviate.SearchResult
	var err error

	// 根据 alpha 值选择检索方式
	if req.Alpha != nil && *req.Alpha < 1.0 {
		// 混合检索
		weaviateResults, err = s.weaviateClient.HybridSearchPRDs(ctx, req.Query, embedding, req.Limit, req.ScoreThreshold, *req.Alpha, filters)
	} else {
		// 纯向量检索
		weaviateResults, err = s.weaviateClient.SearchPRDs(ctx, embedding, req.Limit, req.ScoreThreshold, filters)
	}

	if err != nil {
		return nil, fmt.Errorf("Weaviate PRD 搜索失败: %w", err)
	}

	// 转换结果
	var results []SearchResult
	for _, wr := range weaviateResults {
		// 从 PostgreSQL 获取完整数据
		prd, err := s.prdRepo.GetByID(wr.ID)
		if err != nil {
			continue // 跳过无法获取的记录
		}

		results = append(results, SearchResult{
			Type:    SearchTypePRD,
			ID:      prd.ID,
			Title:   prd.Title,
			Content: s.truncateContent(prd.Content, 200),
			Score:   wr.Score,
			Metadata: map[string]interface{}{
				"code":           prd.Code,
				"status":         prd.Status,
				"version":        prd.Version,
				"module_id":      prd.ModuleID,
				"app_version_id": prd.AppVersionID,
				"created_at":     prd.CreatedAt,
			},
			Highlights: s.extractHighlights(prd.Content, req.Query, 3),
		})
	}

	return results, nil
}

// searchTestCases 搜索测试用例
func (s *SearchService) searchTestCases(ctx context.Context, embedding []float32, req *SearchRequest) ([]SearchResult, error) {
	// 构建过滤条件
	filters := s.buildTestCaseFilters(req)

	var weaviateResults []weaviate.SearchResult
	var err error

	// 根据 alpha 值选择检索方式
	if req.Alpha != nil && *req.Alpha < 1.0 {
		// 混合检索
		weaviateResults, err = s.weaviateClient.HybridSearchTestCases(ctx, req.Query, embedding, req.Limit, req.ScoreThreshold, *req.Alpha, filters)
	} else {
		// 纯向量检索
		weaviateResults, err = s.weaviateClient.SearchTestCases(ctx, embedding, req.Limit, req.ScoreThreshold, filters)
	}

	if err != nil {
		return nil, fmt.Errorf("Weaviate 测试用例搜索失败: %w", err)
	}

	// 转换结果
	var results []SearchResult
	for _, wr := range weaviateResults {
		// 从 PostgreSQL 获取完整数据
		testcase, err := s.testcaseRepo.GetByID(wr.ID)
		if err != nil {
			continue // 跳过无法获取的记录
		}

		results = append(results, SearchResult{
			Type:    SearchTypeTestCase,
			ID:      testcase.ID,
			Title:   testcase.Title,
			Content: s.buildTestCaseContent(testcase),
			Score:   wr.Score,
			Metadata: map[string]interface{}{
				"code":           testcase.Code,
				"priority":       testcase.Priority,
				"type":           testcase.Type,
				"status":         testcase.Status,
				"module_id":      testcase.ModuleID,
				"prd_id":         testcase.PRDID,
				"app_version_id": testcase.AppVersionID,
				"created_at":     testcase.CreatedAt,
			},
			Highlights: []string{testcase.Title},
		})
	}

	return results, nil
}

// buildPRDFilters 构建 PRD 过滤条件
func (s *SearchService) buildPRDFilters(req *SearchRequest) map[string]interface{} {
	filters := make(map[string]interface{})

	if req.ProjectID != "" {
		filters["project_id"] = req.ProjectID
	}
	if req.ModuleID != nil {
		filters["module_id"] = *req.ModuleID
	}
	if req.AppVersionID != nil {
		filters["app_version_id"] = *req.AppVersionID
	}
	if req.Status != nil {
		filters["status"] = *req.Status
	}

	return filters
}

// buildTestCaseFilters 构建测试用例过滤条件
func (s *SearchService) buildTestCaseFilters(req *SearchRequest) map[string]interface{} {
	filters := make(map[string]interface{})

	if req.ProjectID != "" {
		filters["project_id"] = req.ProjectID
	}
	if req.ModuleID != nil {
		filters["module_id"] = *req.ModuleID
	}
	if req.AppVersionID != nil {
		filters["app_version_id"] = *req.AppVersionID
	}
	if req.Status != nil {
		filters["status"] = *req.Status
	}

	return filters
}

// buildTestCaseContent 构建测试用例内容摘要
func (s *SearchService) buildTestCaseContent(tc *testcase.TestCase) string {
	// 构建内容摘要：前置条件 + 预期结果
	content := ""
	if tc.Precondition != "" {
		content += "前置条件: " + s.truncateContent(tc.Precondition, 100) + "\n"
	}
	if tc.ExpectedResult != "" {
		content += "预期结果: " + s.truncateContent(tc.ExpectedResult, 100)
	}
	
	return content
}

// truncateContent 截断内容
func (s *SearchService) truncateContent(content string, maxLen int) string {
	runes := []rune(content)
	if len(runes) <= maxLen {
		return content
	}
	return string(runes[:maxLen]) + "..."
}

// extractHighlights 提取高亮片段
func (s *SearchService) extractHighlights(content, query string, count int) []string {
	// 简化实现：将内容分成多个片段
	// 在实际生产环境中，可以使用更智能的算法（如 BM25）来提取包含查询关键词的片段
	highlights := []string{}
	runes := []rune(content)
	
	if len(runes) == 0 {
		return highlights
	}

	chunkSize := 150 // 每个片段的字符数

	for i := 0; i < count && i*chunkSize < len(runes); i++ {
		start := i * chunkSize
		end := start + chunkSize
		if end > len(runes) {
			end = len(runes)
		}
		
		chunk := string(runes[start:end])
		if end < len(runes) {
			chunk += "..."
		}
		highlights = append(highlights, chunk)
	}

	return highlights
}

// sortAndLimitResults 排序并限制结果
func (s *SearchService) sortAndLimitResults(results []SearchResult, limit int) []SearchResult {
	// 按分数降序排序
	for i := 0; i < len(results)-1; i++ {
		for j := i + 1; j < len(results); j++ {
			if results[i].Score < results[j].Score {
				results[i], results[j] = results[j], results[i]
			}
		}
	}

	// 限制结果数量
	if len(results) > limit {
		results = results[:limit]
	}

	return results
}


// GetRecommendations 获取相关推荐
func (s *SearchService) GetRecommendations(ctx context.Context, projectID, docType, docID string, limit int) (*SearchResponse, error) {
	var embedding []float32
	var err error
	var searchType SearchType
	
	embeddingService := s.embeddingManager.GetService()
	if embeddingService == nil {
		return nil, fmt.Errorf("Embedding 服务未初始化")
	}

	// 根据文档类型获取文档并生成向量
	switch docType {
	case "prd":
		prd, err := s.prdRepo.GetByID(docID)
		if err != nil {
			return nil, fmt.Errorf("获取 PRD 失败: %w", err)
		}
		// 使用 PRD 的 title + content 生成向量
		text := prd.Title + "\n" + prd.Content
		embedding, err = embeddingService.Embed(ctx, text)
		if err != nil {
			return nil, fmt.Errorf("生成向量失败: %w", err)
		}
		searchType = SearchTypeAll // 推荐所有类型

	case "testcase":
		testcase, err := s.testcaseRepo.GetByID(docID)
		if err != nil {
			return nil, fmt.Errorf("获取测试用例失败: %w", err)
		}
		// 使用测试用例的 title 生成向量
		embedding, err = embeddingService.Embed(ctx, testcase.Title)
		if err != nil {
			return nil, fmt.Errorf("生成向量失败: %w", err)
		}
		searchType = SearchTypeAll // 推荐所有类型

	default:
		return nil, fmt.Errorf("不支持的文档类型: %s", docType)
	}

	// 构建搜索请求
	req := &SearchRequest{
		Query:          "", // 不需要查询文本，直接使用向量
		Type:           searchType,
		Limit:          limit + 1, // 多获取一个，用于排除自己
		ScoreThreshold: 0.7,
		ProjectID:      projectID,
	}

	// 搜索相似文档
	var results []SearchResult

	// 搜索 PRD
	prdResults, err := s.searchPRDs(ctx, embedding, req)
	if err != nil {
		return nil, err
	}

	// 搜索测试用例
	testcaseResults, err := s.searchTestCases(ctx, embedding, req)
	if err != nil {
		return nil, err
	}

	// 合并结果
	results = append(results, prdResults...)
	results = append(results, testcaseResults...)

	// 排除自己
	var filteredResults []SearchResult
	for _, r := range results {
		if r.ID != docID {
			filteredResults = append(filteredResults, r)
		}
	}

	// 排序并限制结果
	filteredResults = s.sortAndLimitResults(filteredResults, limit)

	return &SearchResponse{
		Results: filteredResults,
		Total:   len(filteredResults),
		Query:   fmt.Sprintf("基于 %s 的推荐", docType),
		Type:    searchType,
	}, nil
}
