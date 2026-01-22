package settings

import (
	"context"
	"fmt"

	"gorm.io/gorm"
)

// SettingsService 设置服务
type SettingsService struct {
	db *gorm.DB
}

// NewSettingsService 创建设置服务
func NewSettingsService(db *gorm.DB) *SettingsService {
	return &SettingsService{
		db: db,
	}
}

// GlobalSetting 全局设置
type GlobalSetting struct {
	ID          string `json:"id"`
	Key         string `json:"key"`
	Value       string `json:"value"`
	Type        string `json:"type"`
	Description string `json:"description"`
}

// GetSettings 获取所有设置
func (s *SettingsService) GetSettings(ctx context.Context) ([]GlobalSetting, error) {
	var settings []GlobalSetting
	err := s.db.WithContext(ctx).
		Table("global_settings").
		Select("id, key, value, type, description").
		Order("key").
		Find(&settings).Error

	if err != nil {
		return nil, fmt.Errorf("获取设置失败: %w", err)
	}

	return settings, nil
}

// GetSettingsByCategory 按类别获取设置
func (s *SettingsService) GetSettingsByCategory(ctx context.Context, category string) ([]GlobalSetting, error) {
	var settings []GlobalSetting
	
	// 根据类别前缀过滤
	pattern := category + "_%"
	err := s.db.WithContext(ctx).
		Table("global_settings").
		Select("id, key, value, type, description").
		Where("key LIKE ?", pattern).
		Order("key").
		Find(&settings).Error

	if err != nil {
		return nil, fmt.Errorf("获取设置失败: %w", err)
	}

	return settings, nil
}

// UpdateSetting 更新设置
func (s *SettingsService) UpdateSetting(ctx context.Context, key string, value string) error {
	result := s.db.WithContext(ctx).
		Table("global_settings").
		Where("key = ?", key).
		Update("value", value)

	if result.Error != nil {
		return fmt.Errorf("更新设置失败: %w", result.Error)
	}

	if result.RowsAffected == 0 {
		return fmt.Errorf("设置不存在: %s", key)
	}

	return nil
}

// BatchUpdateSettings 批量更新设置
func (s *SettingsService) BatchUpdateSettings(ctx context.Context, updates map[string]string) error {
	// 使用事务
	return s.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
		for key, value := range updates {
			result := tx.Table("global_settings").
				Where("key = ?", key).
				Update("value", value)

			if result.Error != nil {
				return fmt.Errorf("更新设置 %s 失败: %w", key, result.Error)
			}

			if result.RowsAffected == 0 {
				return fmt.Errorf("设置不存在: %s", key)
			}
		}
		return nil
	})
}

// GetSettingValue 获取单个设置的值
func (s *SettingsService) GetSettingValue(ctx context.Context, key string) (string, error) {
	var value string
	err := s.db.WithContext(ctx).
		Table("global_settings").
		Select("value").
		Where("key = ?", key).
		Scan(&value).Error

	if err != nil {
		return "", fmt.Errorf("获取设置失败: %w", err)
	}

	return value, nil
}
