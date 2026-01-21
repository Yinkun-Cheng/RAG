package weaviate

import (
	"context"
	"fmt"
	"time"

	"rag-backend/internal/pkg/weaviate"
)

// VectorRepository 向量数据仓库接口
type VectorRepository interface {
	// PRD 相关
	SyncPRD(ctx context.Context, prdID, projectID string, moduleID *string, title, content, status string, createdAt time.Time) error
	DeletePRD(ctx context.Context, prdID string) error

	// 测试用例相关
	SyncTestCase(ctx context.Context, testCaseID, projectID string, moduleID, prdID *string, title, priority, typeStr, status string, createdAt time.Time) error
	DeleteTestCase(ctx context.Context, testCaseID string) error
}

type vectorRepository struct {
	client           *weaviate.Client
	embeddingService weaviate.EmbeddingService
}

// NewVectorRepository 创建向量数据仓库
func NewVectorRepository(client *weaviate.Client, embeddingService weaviate.EmbeddingService) VectorRepository {
	return &vectorRepository{
		client:           client,
		embeddingService: embeddingService,
	}
}

// SyncPRD 同步 PRD 到 Weaviate
func (r *vectorRepository) SyncPRD(ctx context.Context, prdID, projectID string, moduleID *string, title, content, status string, createdAt time.Time) error {
	// 向量化：title + content
	textToEmbed := fmt.Sprintf("%s\n\n%s", title, content)
	embedding, err := r.embeddingService.Embed(ctx, textToEmbed)
	if err != nil {
		return fmt.Errorf("failed to embed PRD: %w", err)
	}

	// 同步到 Weaviate
	data := &weaviate.PRDDocumentData{
		PRDID:     prdID,
		ProjectID: projectID,
		ModuleID:  moduleID,
		Title:     title,
		Content:   content,
		Status:    status,
		CreatedAt: createdAt,
	}

	if err := r.client.SyncPRDDocument(ctx, data, embedding); err != nil {
		return fmt.Errorf("failed to sync PRD to Weaviate: %w", err)
	}

	return nil
}

// DeletePRD 从 Weaviate 删除 PRD
func (r *vectorRepository) DeletePRD(ctx context.Context, prdID string) error {
	if err := r.client.DeletePRDDocument(ctx, prdID); err != nil {
		return fmt.Errorf("failed to delete PRD from Weaviate: %w", err)
	}
	return nil
}

// SyncTestCase 同步测试用例到 Weaviate
func (r *vectorRepository) SyncTestCase(ctx context.Context, testCaseID, projectID string, moduleID, prdID *string, title, priority, typeStr, status string, createdAt time.Time) error {
	// 向量化：仅 title（标题已经很具体）
	embedding, err := r.embeddingService.Embed(ctx, title)
	if err != nil {
		return fmt.Errorf("failed to embed test case: %w", err)
	}

	// 同步到 Weaviate
	data := &weaviate.TestCaseData{
		TestCaseID: testCaseID,
		ProjectID:  projectID,
		ModuleID:   moduleID,
		PRDID:      prdID,
		Title:      title,
		Priority:   priority,
		Type:       typeStr,
		Status:     status,
		CreatedAt:  createdAt,
	}

	if err := r.client.SyncTestCase(ctx, data, embedding); err != nil {
		return fmt.Errorf("failed to sync test case to Weaviate: %w", err)
	}

	return nil
}

// DeleteTestCase 从 Weaviate 删除测试用例
func (r *vectorRepository) DeleteTestCase(ctx context.Context, testCaseID string) error {
	if err := r.client.DeleteTestCase(ctx, testCaseID); err != nil {
		return fmt.Errorf("failed to delete test case from Weaviate: %w", err)
	}
	return nil
}
