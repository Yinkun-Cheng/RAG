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
	db              *gorm.DB
	currentService  EmbeddingService
	mu              sync.RWMutex
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

	switch config.Provider {
	case "openai":
		if config.APIKey == "" {
			log.Println("Warning: OpenAI API Key is empty, falling back to Mock service")
			service = NewMockEmbeddingService()
		} else {
			service = NewOpenAIEmbeddingService(config.APIKey, config.BaseURL, config.Model)
			log.Printf("Initialized OpenAI Embedding Service (model: %s)", config.Model)
		}
	case "volcano_ark", "volcengine": // 支持两种写法（向后兼容）
		if config.APIKey == "" {
			log.Println("Warning: Volcano Ark API Key is empty, falling back to Mock service")
			service = NewMockEmbeddingService()
		} else {
			service = NewVolcanoArkEmbeddingService(config.APIKey, config.BaseURL, config.Model)
			log.Printf("Initialized Volcano Ark Embedding Service (model: %s, provider: %s)", config.Model, config.Provider)
		}
	case "mock":
		service = NewMockEmbeddingService()
		log.Println("Initialized Mock Embedding Service (for testing)")
	default:
		log.Printf("Unknown embedding provider: %s, falling back to Mock service", config.Provider)
		service = NewMockEmbeddingService()
	}

	m.mu.Lock()
	m.currentService = service
	m.mu.Unlock()

	return nil
}

// GetService 获取当前的 Embedding 服务
func (m *EmbeddingManager) GetService() EmbeddingService {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.currentService
}

// ReloadService 重新加载 Embedding 服务（配置变更后调用）
func (m *EmbeddingManager) ReloadService(ctx context.Context) error {
	log.Println("Reloading Embedding Service...")
	return m.InitializeService(ctx)
}
