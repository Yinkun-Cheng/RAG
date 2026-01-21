package weaviate

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"time"
)

// EmbeddingService 向量化服务接口
type EmbeddingService interface {
	Embed(ctx context.Context, text string) ([]float32, error)
	EmbedBatch(ctx context.Context, texts []string) ([][]float32, error)
}

// OpenAIEmbeddingService OpenAI Embedding 服务
type OpenAIEmbeddingService struct {
	apiKey  string
	baseURL string
	model   string
	client  *http.Client
}

// OpenAIEmbeddingRequest OpenAI Embedding API 请求
type OpenAIEmbeddingRequest struct {
	Input string `json:"input"`
	Model string `json:"model"`
}

// OpenAIEmbeddingResponse OpenAI Embedding API 响应
type OpenAIEmbeddingResponse struct {
	Data []struct {
		Embedding []float32 `json:"embedding"`
		Index     int       `json:"index"`
	} `json:"data"`
	Model string `json:"model"`
	Usage struct {
		PromptTokens int `json:"prompt_tokens"`
		TotalTokens  int `json:"total_tokens"`
	} `json:"usage"`
}

// NewOpenAIEmbeddingService 创建 OpenAI Embedding 服务
func NewOpenAIEmbeddingService(apiKey, baseURL, model string) *OpenAIEmbeddingService {
	if baseURL == "" {
		baseURL = "https://api.openai.com/v1"
	}
	if model == "" {
		model = "text-embedding-ada-002"
	}

	return &OpenAIEmbeddingService{
		apiKey:  apiKey,
		baseURL: baseURL,
		model:   model,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Embed 向量化单个文本
func (s *OpenAIEmbeddingService) Embed(ctx context.Context, text string) ([]float32, error) {
	reqBody := OpenAIEmbeddingRequest{
		Input: text,
		Model: s.model,
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", s.baseURL+"/embeddings", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+s.apiKey)

	resp, err := s.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("embedding API returned status %d: %s", resp.StatusCode, string(body))
	}

	var embeddingResp OpenAIEmbeddingResponse
	if err := json.NewDecoder(resp.Body).Decode(&embeddingResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if len(embeddingResp.Data) == 0 {
		return nil, fmt.Errorf("no embedding data returned")
	}

	return embeddingResp.Data[0].Embedding, nil
}

// EmbedBatch 批量向量化文本
func (s *OpenAIEmbeddingService) EmbedBatch(ctx context.Context, texts []string) ([][]float32, error) {
	// 简单实现：逐个调用（生产环境可以优化为真正的批量调用）
	embeddings := make([][]float32, len(texts))
	for i, text := range texts {
		embedding, err := s.Embed(ctx, text)
		if err != nil {
			return nil, fmt.Errorf("failed to embed text %d: %w", i, err)
		}
		embeddings[i] = embedding
	}
	return embeddings, nil
}

// VolcanoArkEmbeddingService 火山引擎 Ark Embedding 服务
type VolcanoArkEmbeddingService struct {
	apiKey  string
	baseURL string
	model   string
	client  *http.Client
}

// VolcanoArkEmbeddingRequest 火山引擎 Ark Embedding API 请求
type VolcanoArkEmbeddingRequest struct {
	Model string                   `json:"model"`
	Input []map[string]interface{} `json:"input"`
}

// VolcanoArkEmbeddingResponse 火山引擎 Ark Embedding API 响应
type VolcanoArkEmbeddingResponse struct {
	Data struct {
		Embedding []float32 `json:"embedding"`
		Object    string    `json:"object"`
	} `json:"data"`
	Model string `json:"model"`
	Usage struct {
		PromptTokens int `json:"prompt_tokens"`
		TotalTokens  int `json:"total_tokens"`
	} `json:"usage"`
}

// NewVolcanoArkEmbeddingService 创建火山引擎 Ark Embedding 服务
func NewVolcanoArkEmbeddingService(apiKey, baseURL, model string) *VolcanoArkEmbeddingService {
	if baseURL == "" {
		baseURL = "https://ark.cn-beijing.volces.com"
	}
	if model == "" {
		model = "ep-20260121110525-5mmss"
	}

	return &VolcanoArkEmbeddingService{
		apiKey:  apiKey,
		baseURL: baseURL,
		model:   model,
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
	}
}

// Embed 向量化单个文本
func (s *VolcanoArkEmbeddingService) Embed(ctx context.Context, text string) ([]float32, error) {
	// 火山引擎 Ark API 使用多模态格式
	reqBody := VolcanoArkEmbeddingRequest{
		Model: s.model,
		Input: []map[string]interface{}{
			{
				"type": "text",
				"text": text,
			},
		},
	}

	jsonData, err := json.Marshal(reqBody)
	if err != nil {
		return nil, fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, "POST", s.baseURL+"/api/v3/embeddings/multimodal", bytes.NewBuffer(jsonData))
	if err != nil {
		return nil, fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("Authorization", "Bearer "+s.apiKey)

	resp, err := s.client.Do(req)
	if err != nil {
		return nil, fmt.Errorf("failed to send request: %w", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		body, _ := io.ReadAll(resp.Body)
		return nil, fmt.Errorf("embedding API returned status %d: %s", resp.StatusCode, string(body))
	}

	var embeddingResp VolcanoArkEmbeddingResponse
	if err := json.NewDecoder(resp.Body).Decode(&embeddingResp); err != nil {
		return nil, fmt.Errorf("failed to decode response: %w", err)
	}

	if len(embeddingResp.Data.Embedding) == 0 {
		return nil, fmt.Errorf("no embedding data returned")
	}

	return embeddingResp.Data.Embedding, nil
}

// EmbedBatch 批量向量化文本
func (s *VolcanoArkEmbeddingService) EmbedBatch(ctx context.Context, texts []string) ([][]float32, error) {
	// 简单实现：逐个调用（生产环境可以优化为真正的批量调用）
	embeddings := make([][]float32, len(texts))
	for i, text := range texts {
		embedding, err := s.Embed(ctx, text)
		if err != nil {
			return nil, fmt.Errorf("failed to embed text %d: %w", i, err)
		}
		embeddings[i] = embedding
	}
	return embeddings, nil
}

// MockEmbeddingService Mock Embedding 服务（用于测试）
type MockEmbeddingService struct{}

// NewMockEmbeddingService 创建 Mock Embedding 服务
func NewMockEmbeddingService() *MockEmbeddingService {
	return &MockEmbeddingService{}
}

// Embed Mock 向量化（返回固定长度的随机向量）
func (s *MockEmbeddingService) Embed(ctx context.Context, text string) ([]float32, error) {
	// 返回 1536 维的 Mock 向量（OpenAI text-embedding-ada-002 的维度）
	embedding := make([]float32, 1536)
	for i := range embedding {
		embedding[i] = 0.1 // 简单的 Mock 值
	}
	return embedding, nil
}

// EmbedBatch Mock 批量向量化
func (s *MockEmbeddingService) EmbedBatch(ctx context.Context, texts []string) ([][]float32, error) {
	embeddings := make([][]float32, len(texts))
	for i := range texts {
		embedding, err := s.Embed(ctx, texts[i])
		if err != nil {
			return nil, err
		}
		embeddings[i] = embedding
	}
	return embeddings, nil
}
