package handler

import (
	"net/http"
	"rag-backend/internal/domain/common"
	"rag-backend/internal/service/settings"

	"github.com/gin-gonic/gin"
)

// SettingsHandler 设置处理器
type SettingsHandler struct {
	settingsService *settings.SettingsService
}

// NewSettingsHandler 创建设置处理器
func NewSettingsHandler(settingsService *settings.SettingsService) *SettingsHandler {
	return &SettingsHandler{
		settingsService: settingsService,
	}
}

// GetAllSettings 获取所有设置
// @Summary 获取所有全局设置
// @Description 获取所有全局配置项
// @Tags Settings
// @Accept json
// @Produce json
// @Success 200 {object} common.Response{data=[]settings.GlobalSetting}
// @Router /api/v1/settings [get]
func (h *SettingsHandler) GetAllSettings(c *gin.Context) {
	settings, err := h.settingsService.GetSettings(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "获取设置失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(settings))
}

// GetSettingsByCategory 按类别获取设置
// @Summary 按类别获取设置
// @Description 按类别前缀获取配置项（如 embedding, search）
// @Tags Settings
// @Accept json
// @Produce json
// @Param category path string true "类别名称（embedding/search）"
// @Success 200 {object} common.Response{data=[]settings.GlobalSetting}
// @Router /api/v1/settings/{category} [get]
func (h *SettingsHandler) GetSettingsByCategory(c *gin.Context) {
	category := c.Param("category")

	settings, err := h.settingsService.GetSettingsByCategory(c.Request.Context(), category)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "获取设置失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(settings))
}

// UpdateSetting 更新单个设置
// @Summary 更新单个设置
// @Description 更新指定的配置项
// @Tags Settings
// @Accept json
// @Produce json
// @Param key path string true "设置键名"
// @Param request body map[string]string true "设置值"
// @Success 200 {object} common.Response
// @Router /api/v1/settings/{key} [put]
func (h *SettingsHandler) UpdateSetting(c *gin.Context) {
	key := c.Param("key")

	var req struct {
		Value string `json:"value" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(http.StatusBadRequest, "参数错误", err.Error()))
		return
	}

	err := h.settingsService.UpdateSetting(c.Request.Context(), key, req.Value)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "更新设置失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "设置更新成功",
	}))
}

// BatchUpdateSettings 批量更新设置
// @Summary 批量更新设置
// @Description 批量更新多个配置项
// @Tags Settings
// @Accept json
// @Produce json
// @Param request body map[string]string true "设置键值对"
// @Success 200 {object} common.Response
// @Router /api/v1/settings/batch [put]
func (h *SettingsHandler) BatchUpdateSettings(c *gin.Context) {
	var updates map[string]string

	if err := c.ShouldBindJSON(&updates); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(http.StatusBadRequest, "参数错误", err.Error()))
		return
	}

	err := h.settingsService.BatchUpdateSettings(c.Request.Context(), updates)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "批量更新设置失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "设置批量更新成功",
	}))
}
