package weaviate

import (
	"context"
	"fmt"
	"log"
	"time"

	"github.com/weaviate/weaviate-go-client/v4/weaviate/filters"
	"github.com/weaviate/weaviate-go-client/v4/weaviate/graphql"
)

// PRDDocumentData PRD 文档数据（用于同步到 Weaviate）
type PRDDocumentData struct {
	PRDID     string
	ProjectID string
	ModuleID  *string
	Title     string
	Content   string
	Status    string
	CreatedAt time.Time
}

// TestCaseData 测试用例数据（用于同步到 Weaviate）
type TestCaseData struct {
	TestCaseID string
	ProjectID  string
	ModuleID   *string
	PRDID      *string
	Title      string
	Priority   string
	Type       string
	Status     string
	CreatedAt  time.Time
}

// SyncPRDDocument 同步 PRD 文档到 Weaviate
func (c *Client) SyncPRDDocument(ctx context.Context, data *PRDDocumentData, embedding []float32) error {
	// 验证向量维度
	if len(embedding) == 0 {
		return fmt.Errorf("embedding vector is empty")
	}
	
	log.Printf("📝 Syncing PRD %s with embedding dimension: %d", data.PRDID, len(embedding))
	
	// 检查是否已存在
	exists, weaviateID, err := c.checkPRDExists(ctx, data.PRDID)
	if err != nil {
		return fmt.Errorf("failed to check PRD existence: %w", err)
	}

	// 构建属性
	properties := map[string]interface{}{
		"prd_id":     data.PRDID,
		"project_id": data.ProjectID,
		"title":      data.Title,
		"content":    data.Content, // ✅ 添加 content 字段用于 BM25 检索
		"status":     data.Status,
		"created_at": data.CreatedAt.Format(time.RFC3339),
	}

	if data.ModuleID != nil {
		properties["module_id"] = *data.ModuleID
	}

	if exists {
		// 更新现有数据
		if err := c.updateObject(ctx, weaviateID, PRDDocumentClass, properties, embedding); err != nil {
			return fmt.Errorf("failed to update PRD: %w", err)
		}
		log.Printf("✅ PRD %s updated in Weaviate", data.PRDID)
	} else {
		// 创建新数据
		if err := c.createObject(ctx, PRDDocumentClass, properties, embedding); err != nil {
			return fmt.Errorf("failed to create PRD: %w", err)
		}
		log.Printf("✅ PRD %s created in Weaviate", data.PRDID)
	}

	return nil
}

// SyncTestCase 同步测试用例到 Weaviate
func (c *Client) SyncTestCase(ctx context.Context, data *TestCaseData, embedding []float32) error {
	// 验证向量维度
	if len(embedding) == 0 {
		return fmt.Errorf("embedding vector is empty")
	}
	
	log.Printf("📝 Syncing TestCase %s with embedding dimension: %d", data.TestCaseID, len(embedding))
	
	// 检查是否已存在
	exists, weaviateID, err := c.checkTestCaseExists(ctx, data.TestCaseID)
	if err != nil {
		return fmt.Errorf("failed to check test case existence: %w", err)
	}

	// 构建属性
	properties := map[string]interface{}{
		"test_case_id": data.TestCaseID,
		"project_id":   data.ProjectID,
		"title":        data.Title,
		"priority":     data.Priority,
		"type":         data.Type,
		"status":       data.Status,
		"created_at":   data.CreatedAt.Format(time.RFC3339),
	}

	if data.ModuleID != nil {
		properties["module_id"] = *data.ModuleID
	}

	if data.PRDID != nil {
		properties["prd_id"] = *data.PRDID
	}

	if exists {
		// 更新现有数据
		if err := c.updateObject(ctx, weaviateID, TestCaseClass, properties, embedding); err != nil {
			return fmt.Errorf("failed to update test case: %w", err)
		}
		log.Printf("✅ Test case %s updated in Weaviate", data.TestCaseID)
	} else {
		// 创建新数据
		if err := c.createObject(ctx, TestCaseClass, properties, embedding); err != nil {
			return fmt.Errorf("failed to create test case: %w", err)
		}
		log.Printf("✅ Test case %s created in Weaviate", data.TestCaseID)
	}

	return nil
}

// DeletePRDDocument 从 Weaviate 删除 PRD 文档
func (c *Client) DeletePRDDocument(ctx context.Context, prdID string) error {
	exists, weaviateID, err := c.checkPRDExists(ctx, prdID)
	if err != nil {
		return fmt.Errorf("failed to check PRD existence: %w", err)
	}

	if !exists {
		log.Printf("PRD %s not found in Weaviate, skipping deletion", prdID)
		return nil
	}

	if err := c.deleteObject(ctx, weaviateID); err != nil {
		return fmt.Errorf("failed to delete PRD: %w", err)
	}

	log.Printf("PRD %s deleted from Weaviate", prdID)
	return nil
}

// DeleteTestCase 从 Weaviate 删除测试用例
func (c *Client) DeleteTestCase(ctx context.Context, testCaseID string) error {
	exists, weaviateID, err := c.checkTestCaseExists(ctx, testCaseID)
	if err != nil {
		return fmt.Errorf("failed to check test case existence: %w", err)
	}

	if !exists {
		log.Printf("Test case %s not found in Weaviate, skipping deletion", testCaseID)
		return nil
	}

	if err := c.deleteObject(ctx, weaviateID); err != nil {
		return fmt.Errorf("failed to delete test case: %w", err)
	}

	log.Printf("Test case %s deleted from Weaviate", testCaseID)
	return nil
}

// checkPRDExists 检查 PRD 是否存在于 Weaviate
func (c *Client) checkPRDExists(ctx context.Context, prdID string) (bool, string, error) {
	where := filters.Where().
		WithPath([]string{"prd_id"}).
		WithOperator(filters.Equal).
		WithValueText(prdID)

	result, err := c.client.GraphQL().Get().
		WithClassName(PRDDocumentClass).
		WithFields(graphql.Field{Name: "_additional { id }"}).
		WithWhere(where).
		Do(ctx)

	if err != nil {
		return false, "", err
	}

	data, ok := result.Data["Get"].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	items, ok := data[PRDDocumentClass].([]interface{})
	if !ok || len(items) == 0 {
		return false, "", nil
	}

	firstItem, ok := items[0].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	additional, ok := firstItem["_additional"].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	id, ok := additional["id"].(string)
	if !ok {
		return false, "", nil
	}

	return true, id, nil
}

// checkTestCaseExists 检查测试用例是否存在于 Weaviate
func (c *Client) checkTestCaseExists(ctx context.Context, testCaseID string) (bool, string, error) {
	where := filters.Where().
		WithPath([]string{"test_case_id"}).
		WithOperator(filters.Equal).
		WithValueText(testCaseID)

	result, err := c.client.GraphQL().Get().
		WithClassName(TestCaseClass).
		WithFields(graphql.Field{Name: "_additional { id }"}).
		WithWhere(where).
		Do(ctx)

	if err != nil {
		return false, "", err
	}

	data, ok := result.Data["Get"].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	items, ok := data[TestCaseClass].([]interface{})
	if !ok || len(items) == 0 {
		return false, "", nil
	}

	firstItem, ok := items[0].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	additional, ok := firstItem["_additional"].(map[string]interface{})
	if !ok {
		return false, "", nil
	}

	id, ok := additional["id"].(string)
	if !ok {
		return false, "", nil
	}

	return true, id, nil
}

// createObject 创建对象
func (c *Client) createObject(ctx context.Context, className string, properties map[string]interface{}, vector []float32) error {
	_, err := c.client.Data().Creator().
		WithClassName(className).
		WithProperties(properties).
		WithVector(vector).
		Do(ctx)

	return err
}

// updateObject 更新对象
func (c *Client) updateObject(ctx context.Context, id, className string, properties map[string]interface{}, vector []float32) error {
	return c.client.Data().Updater().
		WithID(id).
		WithClassName(className).
		WithProperties(properties).
		WithVector(vector).
		Do(ctx)
}

// deleteObject 删除对象
func (c *Client) deleteObject(ctx context.Context, id string) error {
	return c.client.Data().Deleter().
		WithID(id).
		Do(ctx)
}
