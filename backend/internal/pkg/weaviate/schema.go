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
	// 存储：prd_id, project_id, module_id, title, status, created_at
	classObj := &models.Class{
		Class:       PRDDocumentClass,
		Description: "PRD 文档向量存储，用于语义检索",
		Vectorizer:  "none", // 不使用内置向量化，后端自己提供向量
		Properties: []*models.Property{
			{
				Name:        "prd_id",
				DataType:    []string{"text"},
				Description: "PRD 文档 ID（PostgreSQL 主键）",
			},
			{
				Name:        "project_id",
				DataType:    []string{"text"},
				Description: "项目 ID",
			},
			{
				Name:        "module_id",
				DataType:    []string{"text"},
				Description: "模块 ID",
			},
			{
				Name:        "title",
				DataType:    []string{"text"},
				Description: "PRD 标题",
			},
			{
				Name:        "status",
				DataType:    []string{"text"},
				Description: "PRD 状态（draft/published/archived）",
			},
			{
				Name:        "created_at",
				DataType:    []string{"date"},
				Description: "创建时间",
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
		Description: "测试用例向量存储，用于语义检索",
		Vectorizer:  "none", // 不使用内置向量化，后端自己提供向量
		Properties: []*models.Property{
			{
				Name:        "test_case_id",
				DataType:    []string{"text"},
				Description: "测试用例 ID（PostgreSQL 主键）",
			},
			{
				Name:        "project_id",
				DataType:    []string{"text"},
				Description: "项目 ID",
			},
			{
				Name:        "module_id",
				DataType:    []string{"text"},
				Description: "模块 ID",
			},
			{
				Name:        "prd_id",
				DataType:    []string{"text"},
				Description: "关联的 PRD ID",
			},
			{
				Name:        "title",
				DataType:    []string{"text"},
				Description: "测试用例标题",
			},
			{
				Name:        "priority",
				DataType:    []string{"text"},
				Description: "优先级（high/medium/low）",
			},
			{
				Name:        "type",
				DataType:    []string{"text"},
				Description: "类型（functional/performance/security/ui）",
			},
			{
				Name:        "status",
				DataType:    []string{"text"},
				Description: "状态（active/deprecated）",
			},
			{
				Name:        "created_at",
				DataType:    []string{"date"},
				Description: "创建时间",
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
