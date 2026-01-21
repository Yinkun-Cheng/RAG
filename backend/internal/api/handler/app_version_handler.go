package handler

import (
	"net/http"
	"rag-backend/internal/domain/common"
	"rag-backend/internal/domain/project"

	"github.com/gin-gonic/gin"
	"gorm.io/gorm"
)

type AppVersionHandler struct {
	db *gorm.DB
}

func NewAppVersionHandler(db *gorm.DB) *AppVersionHandler {
	return &AppVersionHandler{db: db}
}

// CreateAppVersionRequest 创建 App 版本请求
type CreateAppVersionRequest struct {
	Version     string `json:"version" binding:"required"`
	Description string `json:"description"`
}

// ListAppVersions 获取 App 版本列表
func (h *AppVersionHandler) ListAppVersions(c *gin.Context) {
	projectID := c.Param("id")

	var versions []project.AppVersion
	if err := h.db.Where("project_id = ?", projectID).
		Order("created_at DESC").
		Find(&versions).Error; err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to fetch app versions",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(versions))
}

// CreateAppVersion 创建 App 版本
func (h *AppVersionHandler) CreateAppVersion(c *gin.Context) {
	projectID := c.Param("id")

	var req CreateAppVersionRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			http.StatusBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	// 检查版本是否已存在
	var existing project.AppVersion
	if err := h.db.Where("project_id = ? AND version = ?", projectID, req.Version).
		First(&existing).Error; err == nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			http.StatusBadRequest,
			"Version already exists",
			"",
		))
		return
	}

	// 先生成 UUID
	var newID string
	if err := h.db.Raw("SELECT gen_random_uuid()::VARCHAR").Scan(&newID).Error; err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to generate ID",
			err.Error(),
		))
		return
	}

	version := &project.AppVersion{
		ProjectID:   projectID,
		Version:     req.Version,
		Description: req.Description,
	}
	version.ID = newID

	if err := h.db.Create(version).Error; err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to create app version",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusCreated, common.SuccessResponse(version))
}

// GetAppVersion 获取 App 版本详情
func (h *AppVersionHandler) GetAppVersion(c *gin.Context) {
	projectID := c.Param("id")
	versionID := c.Param("version_id")

	var version project.AppVersion
	if err := h.db.Where("project_id = ? AND id = ?", projectID, versionID).
		First(&version).Error; err != nil {
		if err == gorm.ErrRecordNotFound {
			c.JSON(http.StatusNotFound, common.ErrorResponse(
				http.StatusNotFound,
				"App version not found",
				err.Error(),
			))
			return
		}
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to fetch app version",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(version))
}

// DeleteAppVersion 删除 App 版本
func (h *AppVersionHandler) DeleteAppVersion(c *gin.Context) {
	projectID := c.Param("id")
	versionID := c.Param("version_id")

	// 检查是否有 PRD 使用此版本
	var count int64
	if err := h.db.Table("prd_documents").
		Where("project_id = ? AND app_version_id = ?", projectID, versionID).
		Count(&count).Error; err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to check version usage",
			err.Error(),
		))
		return
	}

	if count > 0 {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			http.StatusBadRequest,
			"Cannot delete version with associated PRDs",
			"",
		))
		return
	}

	if err := h.db.Where("project_id = ? AND id = ?", projectID, versionID).
		Delete(&project.AppVersion{}).Error; err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			http.StatusInternalServerError,
			"Failed to delete app version",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(nil))
}
