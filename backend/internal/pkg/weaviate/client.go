package weaviate

import (
	"context"
	"fmt"
	"log"

	"rag-backend/internal/pkg/config"

	"github.com/weaviate/weaviate-go-client/v4/weaviate"
	"github.com/weaviate/weaviate-go-client/v4/weaviate/auth"
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
