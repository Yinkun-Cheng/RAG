package weaviate

import (
	"context"
	"fmt"
	"log"

	"rag-backend/internal/pkg/config"

	"github.com/weaviate/weaviate-go-client/v4/weaviate"
	"github.com/weaviate/weaviate-go-client/v4/weaviate/auth"
	"github.com/weaviate/weaviate-go-client/v4/weaviate/graphql"
	"github.com/weaviate/weaviate/entities/models"
)

// Client Weaviate 客户端封装
type Client struct {
	client *weaviate.Client
	config *config.WeaviateConfig
}

// NewClient 创建 Weaviate 客户端
func NewClient(cfg *config.WeaviateConfig) (*Client, error) {
	clientConfig := weaviate.Config{
		Host:   fmt.Sprintf("%s:%d", cfg.Host, cfg.Port),
		Scheme: cfg.Scheme,
	}

	// 如果配置了 API Key，添加认证
	if cfg.APIKey != "" {
		clientConfig.AuthConfig = auth.ApiKey{Value: cfg.APIKey}
	}

	client, err := weaviate.NewClient(clientConfig)
	if err != nil {
		return nil, fmt.Errorf("failed to create weaviate client: %w", err)
	}

	log.Printf("Weaviate client created successfully: %s://%s:%d", cfg.Scheme, cfg.Host, cfg.Port)

	return &Client{
		client: client,
		config: cfg,
	}, nil
}

// GetClient 获取原生 Weaviate 客户端
func (c *Client) GetClient() *weaviate.Client {
	return c.client
}

// HealthCheck 健康检查
func (c *Client) HealthCheck(ctx context.Context) error {
	ready, err := c.client.Misc().ReadyChecker().Do(ctx)
	if err != nil {
		return fmt.Errorf("weaviate health check failed: %w", err)
	}

	if !ready {
		return fmt.Errorf("weaviate is not ready")
	}

	log.Println("Weaviate health check passed")
	return nil
}

// Close 关闭客户端连接（Weaviate Go Client 不需要显式关闭）
func (c *Client) Close() error {
	log.Println("Weaviate client closed")
	return nil
}

// SearchResult Weaviate 搜索结果
type SearchResult struct {
	ID    string
	Score float32
}

// SearchPRDs 搜索 PRD 文档
func (c *Client) SearchPRDs(ctx context.Context, embedding []float32, limit int, threshold float32, filters map[string]interface{}) ([]SearchResult, error) {
	// 构建 GraphQL 查询
	nearVector := c.client.GraphQL().NearVectorArgBuilder().
		WithVector(embedding).
		WithCertainty(threshold)

	// 执行查询 - 使用 WithField 逐个添加字段
	result, err := c.client.GraphQL().Get().
		WithClassName("PRDDocument").
		WithFields(
			graphql.Field{Name: "prd_id"},
			graphql.Field{Name: "_additional", Fields: []graphql.Field{
				{Name: "certainty"},
			}},
		).
		WithNearVector(nearVector).
		WithLimit(limit).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("Weaviate PRD 搜索失败: %w", err)
	}

	// 解析结果
	return c.parseSearchResults(result, "PRDDocument", "prd_id")
}

// SearchTestCases 搜索测试用例
func (c *Client) SearchTestCases(ctx context.Context, embedding []float32, limit int, threshold float32, filters map[string]interface{}) ([]SearchResult, error) {
	// 构建 GraphQL 查询
	nearVector := c.client.GraphQL().NearVectorArgBuilder().
		WithVector(embedding).
		WithCertainty(threshold)

	// 执行查询 - 使用 WithField 逐个添加字段
	result, err := c.client.GraphQL().Get().
		WithClassName("TestCase").
		WithFields(
			graphql.Field{Name: "testcase_id"},
			graphql.Field{Name: "_additional", Fields: []graphql.Field{
				{Name: "certainty"},
			}},
		).
		WithNearVector(nearVector).
		WithLimit(limit).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("Weaviate 测试用例搜索失败: %w", err)
	}

	// 解析结果
	return c.parseSearchResults(result, "TestCase", "testcase_id")
}

// HybridSearchPRDs 混合检索 PRD 文档（结合向量检索和 BM25）
func (c *Client) HybridSearchPRDs(ctx context.Context, query string, embedding []float32, limit int, threshold float32, alpha float32, filters map[string]interface{}) ([]SearchResult, error) {
	// 构建混合检索查询
	hybrid := c.client.GraphQL().HybridArgumentBuilder().
		WithQuery(query).
		WithVector(embedding).
		WithAlpha(alpha) // 0 = 纯 BM25, 1 = 纯向量, 0.5 = 各占 50%

	// 执行查询
	result, err := c.client.GraphQL().Get().
		WithClassName("PRDDocument").
		WithFields(
			graphql.Field{Name: "prd_id"},
			graphql.Field{Name: "_additional", Fields: []graphql.Field{
				{Name: "score"},
			}},
		).
		WithHybrid(hybrid).
		WithLimit(limit).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("Weaviate PRD 混合检索失败: %w", err)
	}

	// 解析结果（混合检索使用 score 而不是 certainty）
	return c.parseHybridSearchResults(result, "PRDDocument", "prd_id")
}

// HybridSearchTestCases 混合检索测试用例（结合向量检索和 BM25）
func (c *Client) HybridSearchTestCases(ctx context.Context, query string, embedding []float32, limit int, threshold float32, alpha float32, filters map[string]interface{}) ([]SearchResult, error) {
	// 构建混合检索查询
	hybrid := c.client.GraphQL().HybridArgumentBuilder().
		WithQuery(query).
		WithVector(embedding).
		WithAlpha(alpha) // 0 = 纯 BM25, 1 = 纯向量, 0.5 = 各占 50%

	// 执行查询
	result, err := c.client.GraphQL().Get().
		WithClassName("TestCase").
		WithFields(
			graphql.Field{Name: "testcase_id"},
			graphql.Field{Name: "_additional", Fields: []graphql.Field{
				{Name: "score"},
			}},
		).
		WithHybrid(hybrid).
		WithLimit(limit).
		Do(ctx)

	if err != nil {
		return nil, fmt.Errorf("Weaviate 测试用例混合检索失败: %w", err)
	}

	// 解析结果（混合检索使用 score 而不是 certainty）
	return c.parseHybridSearchResults(result, "TestCase", "testcase_id")
}

// parseSearchResults 解析搜索结果
func (c *Client) parseSearchResults(result *models.GraphQLResponse, className string, idField string) ([]SearchResult, error) {
	if result.Errors != nil && len(result.Errors) > 0 {
		return nil, fmt.Errorf("GraphQL 查询错误: %v", result.Errors[0].Message)
	}

	data, ok := result.Data["Get"].(map[string]interface{})
	if !ok {
		return []SearchResult{}, nil
	}

	items, ok := data[className].([]interface{})
	if !ok {
		return []SearchResult{}, nil
	}

	var results []SearchResult
	for _, item := range items {
		itemMap, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		// 获取 ID
		id, _ := itemMap[idField].(string)

		// 获取相似度分数
		var score float32 = 0
		if additional, ok := itemMap["_additional"].(map[string]interface{}); ok {
			if certainty, ok := additional["certainty"].(float64); ok {
				score = float32(certainty)
			}
		}

		if id != "" {
			results = append(results, SearchResult{
				ID:    id,
				Score: score,
			})
		}
	}

	return results, nil
}

// parseHybridSearchResults 解析混合检索结果
func (c *Client) parseHybridSearchResults(result *models.GraphQLResponse, className string, idField string) ([]SearchResult, error) {
	if result.Errors != nil && len(result.Errors) > 0 {
		return nil, fmt.Errorf("GraphQL 查询错误: %v", result.Errors[0].Message)
	}

	data, ok := result.Data["Get"].(map[string]interface{})
	if !ok {
		return []SearchResult{}, nil
	}

	items, ok := data[className].([]interface{})
	if !ok {
		return []SearchResult{}, nil
	}

	var results []SearchResult
	for _, item := range items {
		itemMap, ok := item.(map[string]interface{})
		if !ok {
			continue
		}

		// 获取 ID
		id, _ := itemMap[idField].(string)

		// 获取混合检索分数（使用 score 而不是 certainty）
		var score float32 = 0
		if additional, ok := itemMap["_additional"].(map[string]interface{}); ok {
			if hybridScore, ok := additional["score"].(float64); ok {
				score = float32(hybridScore)
			}
		}

		if id != "" {
			results = append(results, SearchResult{
				ID:    id,
				Score: score,
			})
		}
	}

	return results, nil
}
