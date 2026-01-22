package weaviate

import (
	"context"
	"fmt"
	"log"
	"sync"

	"gorm.io/gorm"
)

// EmbeddingManager Embedding 服务管理器
type EmbeddingManager struct {
	db                *gorm.DB
	currentService    EmbeddingService
	expectedDimension int // 期望的向量维度
	mu                sync.RWMutex
}

// EmbeddingConfig Embedding 配置（从数据库读取）
type EmbeddingConfig struct {
	Provider string
	APIKey   string
	BaseURL  string
	Model    string
}

// NewEmbeddingManager 创建 Embedding 服务管理器
func NewEmbeddingManager(db *gorm.DB) *EmbeddingManager {
	return &EmbeddingManager{
		db: db,
	}
}

// LoadConfig 从数据库加载 Embedding 配置
func (m *EmbeddingManager) LoadConfig(ctx context.Context) (*EmbeddingConfig, error) {
	var settings []struct {
		Key   string
		Value string
	}

	// 查询 Embedding 相关配置（从 global_settings 表）
	err := m.db.WithContext(ctx).
		Table("global_settings").
		Where("key IN ?", []string{
			"embedding_provider",
			"embedding_api_key",
			"embedding_base_url",
			"embedding_model",
		}).
		Select("key, value").
		Find(&settings).Error

	if err != nil {
		return nil, fmt.Errorf("failed to load embedding config: %w", err)
	}

	config := &EmbeddingConfig{
		Provider: "mock", // 默认使用 mock
		BaseURL:  "https://api.openai.com/v1",
		Model:    "text-embedding-ada-002",
	}

	// 解析配置
	for _, setting := range settings {
		switch setting.Key {
		case "embedding_provider":
			config.Provider = setting.Value
		case "embedding_api_key":
			config.APIKey = setting.Value
		case "embedding_base_url":
			config.BaseURL = setting.Value
		case "embedding_model":
			config.Model = setting.Value
		}
	}

	// 打印加载的配置（用于调试）
	log.Printf("Loaded Embedding Config: Provider=%s, Model=%s, BaseURL=%s, APIKey=%s",
		config.Provider, config.Model, config.BaseURL, maskAPIKey(config.APIKey))

	return config, nil
}

// maskAPIKey 隐藏 API Key 的部分内容（用于日志）
func maskAPIKey(apiKey string) string {
	if apiKey == "" {
		return "<empty>"
	}
	if len(apiKey) <= 8 {
		return "***"
	}
	return apiKey[:4] + "..." + apiKey[len(apiKey)-4:]
}

// InitializeService 初始化 Embedding 服务
func (m *EmbeddingManager) InitializeService(ctx context.Context) error {
	config, err := m.LoadConfig(ctx)
	if err != nil {
		return fmt.Errorf("failed to load config: %w", err)
	}

	var service EmbeddingService
	var expectedDimension int

	switch config.Provider {
	case "openai":
		if config.APIKey == "" {
			log.Println("⚠️  WARNING: OpenAI API Key is empty, falling back to Mock service")
			log.Println("⚠️  Mock service uses 1536-dimensional vectors (OpenAI default)")
			log.Println("⚠️  This may cause dimension mismatch if you switch to a real provider later!")
			service = NewMockEmbeddingService()
			expectedDimension = 1536
		} else {
			service = NewOpenAIEmbeddingService(config.APIKey, config.BaseURL, config.Model)
			expectedDimension = 1536 // OpenAI text-embedding-ada-002 默认维度
			log.Printf("✅ Initialized OpenAI Embedding Service (model: %s, expected dimension: %d)", config.Model, expectedDimension)
		}
	case "volcano_ark", "volcengine": // 支持两种写法（向后兼容）
		if config.APIKey == "" {
			log.Println("⚠️  WARNING: Volcano Ark API Key is empty, falling back to Mock service")
			log.Println("⚠️  Mock service uses 1536-dimensional vectors (OpenAI default)")
			log.Println("⚠️  This may cause dimension mismatch if you switch to a real provider later!")
			service = NewMockEmbeddingService()
			expectedDimension = 1536
		} else {
			service = NewVolcanoArkEmbeddingService(config.APIKey, config.BaseURL, config.Model)
			expectedDimension = 2048 // 火山引擎多模态 Embedding 默认维度
			log.Printf("✅ Initialized Volcano Ark Embedding Service (model: %s, provider: %s, expected dimension: %d)", config.Model, config.Provider, expectedDimension)
		}
	case "mock":
		service = NewMockEmbeddingService()
		expectedDimension = 1536
		log.Println("⚠️  Initialized Mock Embedding Service (for testing, dimension: 1536)")
		log.Println("⚠️  Mock service should NOT be used in production!")
	default:
		log.Printf("⚠️  WARNING: Unknown embedding provider: %s, falling back to Mock service", config.Provider)
		log.Println("⚠️  Mock service uses 1536-dimensional vectors (OpenAI default)")
		log.Println("⚠️  This may cause dimension mismatch if you switch to a real provider later!")
		service = NewMockEmbeddingService()
		expectedDimension = 1536
	}

	m.mu.Lock()
	m.currentService = service
	m.expectedDimension = expectedDimension
	m.mu.Unlock()

	return nil
}

// GetService 获取当前的 Embedding 服务
func (m *EmbeddingManager) GetService() EmbeddingService {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.currentService
}

// GetExpectedDimension 获取期望的向量维度
func (m *EmbeddingManager) GetExpectedDimension() int {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.expectedDimension
}

// ValidateEmbedding 验证向量维度是否正确
func (m *EmbeddingManager) ValidateEmbedding(embedding []float32) error {
	m.mu.RLock()
	expectedDim := m.expectedDimension
	m.mu.RUnlock()

	actualDim := len(embedding)
	if actualDim != expectedDim {
		return fmt.Errorf("❌ Vector dimension mismatch: expected %d, got %d. This usually means:\n"+
			"1. You changed the embedding provider but didn't re-sync Weaviate data\n"+
			"2. The embedding model returned unexpected dimension\n"+
			"Solution: Delete Weaviate schema and re-sync all data with: cd backend && .\\bin\\sync.exe",
			expectedDim, actualDim)
	}
	return nil
}

// ReloadService 重新加载 Embedding 服务（配置变更后调用）
func (m *EmbeddingManager) ReloadService(ctx context.Context) error {
	log.Println("Reloading Embedding Service...")
	return m.InitializeService(ctx)
}
