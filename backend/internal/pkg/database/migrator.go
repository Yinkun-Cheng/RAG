package database

import (
	"rag-backend/internal/domain"

	"go.uber.org/zap"
	"gorm.io/gorm"
)

// AutoMigrate 自动迁移数据库表结构
func AutoMigrate(db *gorm.DB, log *zap.Logger) error {
	log.Info("Starting database auto migration...")

	// 获取所有模型
	models := domain.AllModels()

	// 执行自动迁移
	if err := db.AutoMigrate(models...); err != nil {
		log.Error("Database auto migration failed", zap.Error(err))
		return err
	}

	log.Info("Database auto migration completed successfully")
	return nil
}

// DropAllTables 删除所有表（谨慎使用！）
func DropAllTables(db *gorm.DB, log *zap.Logger) error {
	log.Warn("Dropping all tables...")

	models := domain.AllModels()

	// 反向删除（避免外键约束问题）
	for i := len(models) - 1; i >= 0; i-- {
		if err := db.Migrator().DropTable(models[i]); err != nil {
			log.Error("Failed to drop table", zap.Error(err))
			return err
		}
	}

	log.Info("All tables dropped successfully")
	return nil
}
