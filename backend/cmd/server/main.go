package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"rag-backend/internal/api/middleware"
	"rag-backend/internal/pkg/config"
	"rag-backend/internal/pkg/database"
	"rag-backend/internal/pkg/logger"

	"github.com/gin-gonic/gin"
	"go.uber.org/zap"
)

func main() {
	// Load configuration
	cfg, err := config.Load("config.yaml")
	if err != nil {
		fmt.Printf("Failed to load configuration: %v\n", err)
		os.Exit(1)
	}

	// Initialize logger
	if err := logger.Init(cfg.Logging.Level, cfg.Logging.Format, cfg.Logging.Output); err != nil {
		fmt.Printf("Failed to initialize logger: %v\n", err)
		os.Exit(1)
	}
	defer logger.Sync()

	logger.Info("RAG Test Case Management System - Backend Starting",
		zap.String("mode", cfg.Server.Mode),
		zap.Int("port", cfg.Server.Port))

	// Initialize database connection
	dbConfig := database.PostgresConfig{
		Host:     cfg.Database.Postgres.Host,
		Port:     cfg.Database.Postgres.Port,
		User:     cfg.Database.Postgres.User,
		Password: cfg.Database.Postgres.Password,
		DBName:   cfg.Database.Postgres.DBName,
		SSLMode:  cfg.Database.Postgres.SSLMode,
	}

	db, err := database.NewPostgresDB(dbConfig, logger.Logger())
	if err != nil {
		logger.Fatal("Failed to connect to database", zap.Error(err))
	}
	defer database.Close(db)

	// Database health check
	if err := database.HealthCheck(db); err != nil {
		logger.Fatal("Database health check failed", zap.Error(err))
	}

	// Auto migrate database tables
	if err := database.AutoMigrate(db, logger.Logger()); err != nil {
		logger.Fatal("Database auto migration failed", zap.Error(err))
	}

	// Set Gin mode
	if cfg.Server.Mode == "release" {
		gin.SetMode(gin.ReleaseMode)
	} else {
		gin.SetMode(gin.DebugMode)
	}

	// Initialize Gin router
	router := gin.Default()

	// Apply custom middlewares
	router.Use(middleware.CORS())
	router.Use(middleware.Logger())
	router.Use(middleware.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		// Check database health
		dbHealthy := true
		if err := database.HealthCheck(db); err != nil {
			dbHealthy = false
			logger.Error("Database health check failed", zap.Error(err))
		}

		status := "healthy"
		httpCode := 200
		if !dbHealthy {
			status = "unhealthy"
			httpCode = 503
		}

		c.JSON(httpCode, gin.H{
			"status":   status,
			"message":  "RAG Backend is running",
			"database": dbHealthy,
		})
	})

	// API v1 group
	v1 := router.Group("/api/v1")
	{
		v1.GET("/ping", func(c *gin.Context) {
			c.JSON(200, gin.H{
				"message": "pong",
			})
		})
	}

	// Start server in a goroutine
	go func() {
		addr := fmt.Sprintf(":%d", cfg.Server.Port)
		logger.Info("Server listening", zap.String("address", addr))
		if err := router.Run(addr); err != nil {
			logger.Fatal("Failed to start server", zap.Error(err))
		}
	}()

	// Wait for interrupt signal to gracefully shutdown the server
	quit := make(chan os.Signal, 1)
	signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
	<-quit

	logger.Info("Shutting down server...")
	logger.Info("Server exited")
}
