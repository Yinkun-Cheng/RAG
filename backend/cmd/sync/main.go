package main

import (
	"context"
	"fmt"
	"log"

	"github.com/yourusername/rag-backend/internal/pkg/config"
	"github.com/yourusername/rag-backend/internal/pkg/database"
	"github.com/yourusername/rag-backend/internal/pkg/weaviate"
	"github.com/yourusername/rag-backend/internal/repository/postgres"
	weaviateRepo "github.com/yourusername/rag-backend/internal/repository/weaviate"
)

func main() {
	log.Println("Starting Weaviate sync...")

	// Load config
	cfg, err := config.Load("config.yaml")
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Connect to PostgreSQL
	db, err := database.NewPostgresConnection(cfg.Database.Postgres)
	if err !=