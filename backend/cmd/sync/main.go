package main

import (
	"context"
	"fmt"
	"log"
	"time"

	"rag-backend/internal/domain/prd"
	"rag-backend/internal/domain/testcase"
	"rag-backend/internal/pkg/config"
	"rag-backend/internal/pkg/database"
	"rag-backend/internal/pkg/weaviate"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

func main() {
	log.Println("🚀 Starting Weaviate sync...")
	log.Println("")

	// 加载配置
	cfg, err := config.Load("config.yaml")
	if err != nil {
		log.Fatalf("❌ Failed to load config: %v", err)
	}

	// 连接 PostgreSQL
	log.Println("📦 Connecting to PostgreSQL...")
	dbConfig := database.PostgresConfig{
		Host:     cfg.Database.Postgres.Host,
		Port:     cfg.Database.Postgres.Port,
		User:     cfg.Database.Postgres.User,
		Password: cfg.Database.Postgres.Password,
		DBName:   cfg.Database.Postgres.DBName,
		SSLMode:  cfg.Database.Postgres.SSLMode,
	}
	
	// 创建简单的 logger（不使用 zap）
	db, err := gorm.Open(postgres.Open(fmt.Sprintf(
		"host=%s port=%d user=%s password=%s dbname=%s sslmode=%s",
		dbConfig.Host, dbConfig.Port, dbConfig.User, dbConfig.Password, dbConfig.DBName, dbConfig.SSLMode,
	)), &gorm.Config{})
	if err != nil {
		log.Fatalf("❌ Failed to connect to PostgreSQL: %v", err)
	}
	log.Println("✅ Connected to PostgreSQL")

	// 连接 Weaviate
	log.Println("📦 Connecting to Weaviate...")
	weaviateClient, err := weaviate.NewClient(&cfg.Database.Weaviate)
	if err != nil {
		log.Fatalf("❌ Failed to connect to Weaviate: %v", err)
	}
	defer weaviateClient.Close()
	log.Println("✅ Connected to Weaviate")

	// 初始化 Embedding Manager
	log.Println("🔧 Initializing Embedding Manager...")
	embeddingManager := weaviate.NewEmbeddingManager(db)
	if err := embeddingManager.InitializeService(context.Background()); err != nil {
		log.Fatalf("❌ Failed to initialize embedding manager: %v", err)
	}
	log.Println("")

	// 创建 Schemas（如果不存在）
	log.Println("📋 Creating Weaviate schemas...")
	if err := weaviateClient.CreateSchemas(context.Background()); err != nil {
		log.Fatalf("❌ Failed to create schemas: %v", err)
	}
	log.Println("")

	// 同步 PRD 文档
	log.Println("📄 Syncing PRD documents...")
	if err := syncPRDs(db, weaviateClient, embeddingManager); err != nil {
		log.Fatalf("❌ Failed to sync PRDs: %v", err)
	}
	log.Println("")

	// 同步测试用例
	log.Println("📋 Syncing test cases...")
	if err := syncTestCases(db, weaviateClient, embeddingManager); err != nil {
		log.Fatalf("❌ Failed to sync test cases: %v", err)
	}
	log.Println("")

	log.Println("🎉 Sync completed successfully!")
}

func syncPRDs(db *gorm.DB, client *weaviate.Client, embeddingManager *weaviate.EmbeddingManager) error {
	ctx := context.Background()
	embeddingService := embeddingManager.GetService()

	// 查询所有 PRD
	var prds []prd.PRDDocument
	if err := db.Find(&prds).Error; err != nil {
		return fmt.Errorf("failed to query PRDs: %w", err)
	}

	log.Printf("Found %d PRD documents", len(prds))

	// 同步每个 PRD
	for i, doc := range prds {
		log.Printf("[%d/%d] Syncing PRD: %s", i+1, len(prds), doc.Title)

		// 生成向量：title + content
		textToEmbed := fmt.Sprintf("%s\n\n%s", doc.Title, doc.Content)
		embedding, err := embeddingService.Embed(ctx, textToEmbed)
		if err != nil {
			log.Printf("  ⚠️  Failed to generate embedding: %v", err)
			continue
		}

		// 同步到 Weaviate
		data := &weaviate.PRDDocumentData{
			PRDID:     doc.ID,
			ProjectID: doc.ProjectID,
			ModuleID:  doc.ModuleID,
			Title:     doc.Title,
			Content:   doc.Content,
			Status:    doc.Status,
			CreatedAt: doc.CreatedAt,
		}

		if err := client.SyncPRDDocument(ctx, data, embedding); err != nil {
			log.Printf("  ⚠️  Failed to sync: %v", err)
			continue
		}
	}

	log.Printf("✅ Synced %d PRD documents", len(prds))
	return nil
}

func syncTestCases(db *gorm.DB, client *weaviate.Client, embeddingManager *weaviate.EmbeddingManager) error {
	ctx := context.Background()
	embeddingService := embeddingManager.GetService()

	// 查询所有测试用例
	var testCases []testcase.TestCase
	if err := db.Find(&testCases).Error; err != nil {
		return fmt.Errorf("failed to query test cases: %w", err)
	}

	log.Printf("Found %d test cases", len(testCases))

	// 同步每个测试用例
	for i, tc := range testCases {
		log.Printf("[%d/%d] Syncing TestCase: %s", i+1, len(testCases), tc.Title)

		// 生成向量：仅 title
		embedding, err := embeddingService.Embed(ctx, tc.Title)
		if err != nil {
			log.Printf("  ⚠️  Failed to generate embedding: %v", err)
			continue
		}

		// 同步到 Weaviate
		data := &weaviate.TestCaseData{
			TestCaseID: tc.ID,
			ProjectID:  tc.ProjectID,
			ModuleID:   tc.ModuleID,
			PRDID:      tc.PRDID,
			Title:      tc.Title,
			Priority:   tc.Priority,
			Type:       tc.Type,
			Status:     tc.Status,
			CreatedAt:  tc.CreatedAt,
		}

		if err := client.SyncTestCase(ctx, data, embedding); err != nil {
			log.Printf("  ⚠️  Failed to sync: %v", err)
			continue
		}

		// 避免请求过快
		time.Sleep(10 * time.Millisecond)
	}

	log.Printf("✅ Synced %d test cases", len(testCases))
	return nil
}
