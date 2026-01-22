package weaviate

import (
	"context"
	"fmt"
	"log"

	"github.com/weaviate/weaviate/entities/models"
)

const (
	// PRDDocumentClass PRD 文档 Collection 名称
	PRDDocumentClass = "PRDDocument"
	// TestCaseClass 测试用例 Collection 名称
	TestCaseClass = "TestCase"
)

// CreateSchemas 创建所有 Collection Schema
func (c *Client) CreateSchemas(ctx context.Context) error {
	// 创建 PRDDocument Schema
	if err := c.createPRDDocumentSchema(ctx); err != nil {
		return fmt.Errorf("failed to create PRDDocument schema: %w", err)
	}

	// 创建 TestCase Schema
	if err := c.createTestCaseSchema(ctx); err != nil {
		return fmt.Errorf("failed to create TestCase schema: %w", err)
	}

	log.Println("All Weaviate schemas created successfully")
	return nil
}

// createPRDDocumentSchema 创建 PRDDocument Collection Schema
func (c *Client) createPRDDocumentSchema(ctx context.Context) error {
	// 检查 Schema 是否已存在
	exists, err := c.client.Schema().ClassExistenceChecker().WithClassName(PRDDocumentClass).Do(ctx)
	if err != nil {
		return fmt.Errorf("failed to check schema existence: %w", err)
	}

	if exists {
		log.Printf("Schema %s already exists, skipping creation", PRDDocumentClass)
		return nil
	}

	// 定义 PRDDocument Schema
	// 向量化：title + content
	// 存储：prd_id, project_id, module_id, title, content, status, created_at
	classObj := &models.Class{
		Class:       PRDDocumentClass,
		Description: "PRD 文档向量存储，用于语义检索和混合检索",
		Vectorizer:  "none", // 不使用内置向量化，后端自己提供向量
		VectorIndexConfig: map[string]interface{}{
			"distance": "cosine",
		},
		// 配置 BM25 索引
		InvertedIndexConfig: &models.InvertedIndexConfig{
			Bm25: &models.BM25Config{
				K1: 1.2,
				B:  0.75,
			},
			CleanupIntervalSeconds: 60,
		},
		Properties: []*models.Property{
			{
				Name:            "prd_id",
				DataType:        []string{"text"},
				Description:     "PRD 文档 ID（PostgreSQL 主键）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false), // ID 不需要全文搜索
			},
			{
				Name:            "project_id",
				DataType:        []string{"text"},
				Description:     "项目 ID",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "module_id",
				DataType:        []string{"text"},
				Description:     "模块 ID",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "title",
				DataType:        []string{"text"},
				Description:     "PRD 标题",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(true), // 标题需要全文搜索
				Tokenization:    "word",         // 分词方式
			},
			{
				Name:            "content",
				DataType:        []string{"text"},
				Description:     "PRD 内容（用于 BM25 关键词检索）",
				IndexFilterable: boolPtr(false),
				IndexSearchable: boolPtr(true), // 内容需要全文搜索
				Tokenization:    "word",         // 分词方式
			},
			{
				Name:            "status",
				DataType:        []string{"text"},
				Description:     "PRD 状态（draft/published/archived）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "created_at",
				DataType:        []string{"date"},
				Description:     "创建时间",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
		},
	}

	if err := c.client.Schema().ClassCreator().WithClass(classObj).Do(ctx); err != nil {
		return fmt.Errorf("failed to create class: %w", err)
	}

	log.Printf("Schema %s created successfully", PRDDocumentClass)
	return nil
}

// createTestCaseSchema 创建 TestCase Collection Schema
func (c *Client) createTestCaseSchema(ctx context.Context) error {
	// 检查 Schema 是否已存在
	exists, err := c.client.Schema().ClassExistenceChecker().WithClassName(TestCaseClass).Do(ctx)
	if err != nil {
		return fmt.Errorf("failed to check schema existence: %w", err)
	}

	if exists {
		log.Printf("Schema %s already exists, skipping creation", TestCaseClass)
		return nil
	}

	// 定义 TestCase Schema
	// 向量化：title（标题已经很具体）
	// 存储：test_case_id, project_id, module_id, prd_id, title, priority, type, status, created_at
	classObj := &models.Class{
		Class:       TestCaseClass,
		Description: "测试用例向量存储，用于语义检索和混合检索",
		Vectorizer:  "none", // 不使用内置向量化，后端自己提供向量
		VectorIndexConfig: map[string]interface{}{
			"distance": "cosine",
		},
		// 配置 BM25 索引
		InvertedIndexConfig: &models.InvertedIndexConfig{
			Bm25: &models.BM25Config{
				K1: 1.2,
				B:  0.75,
			},
			CleanupIntervalSeconds: 60,
		},
		Properties: []*models.Property{
			{
				Name:            "test_case_id",
				DataType:        []string{"text"},
				Description:     "测试用例 ID（PostgreSQL 主键）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "project_id",
				DataType:        []string{"text"},
				Description:     "项目 ID",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "module_id",
				DataType:        []string{"text"},
				Description:     "模块 ID",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "prd_id",
				DataType:        []string{"text"},
				Description:     "关联的 PRD ID",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "title",
				DataType:        []string{"text"},
				Description:     "测试用例标题",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(true), // 标题需要全文搜索
				Tokenization:    "word",         // 分词方式
			},
			{
				Name:            "priority",
				DataType:        []string{"text"},
				Description:     "优先级（high/medium/low）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "type",
				DataType:        []string{"text"},
				Description:     "类型（functional/performance/security/ui）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "status",
				DataType:        []string{"text"},
				Description:     "状态（active/deprecated）",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
			{
				Name:            "created_at",
				DataType:        []string{"date"},
				Description:     "创建时间",
				IndexFilterable: boolPtr(true),
				IndexSearchable: boolPtr(false),
			},
		},
	}

	if err := c.client.Schema().ClassCreator().WithClass(classObj).Do(ctx); err != nil {
		return fmt.Errorf("failed to create class: %w", err)
	}

	log.Printf("Schema %s created successfully", TestCaseClass)
	return nil
}

// DeleteSchema 删除指定的 Schema（用于测试或重置）
func (c *Client) DeleteSchema(ctx context.Context, className string) error {
	if err := c.client.Schema().ClassDeleter().WithClassName(className).Do(ctx); err != nil {
		return fmt.Errorf("failed to delete schema %s: %w", className, err)
	}

	log.Printf("Schema %s deleted successfully", className)
	return nil
}

// GetSchema 获取指定的 Schema
func (c *Client) GetSchema(ctx context.Context, className string) (*models.Class, error) {
	class, err := c.client.Schema().ClassGetter().WithClassName(className).Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to get schema %s: %w", className, err)
	}

	return class, nil
}

// ListSchemas 列出所有 Schema
func (c *Client) ListSchemas(ctx context.Context) ([]*models.Class, error) {
	schema, err := c.client.Schema().Getter().Do(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to list schemas: %w", err)
	}

	return schema.Classes, nil
}

// boolPtr 返回 bool 指针（辅助函数）
func boolPtr(b bool) *bool {
	return &b
}
