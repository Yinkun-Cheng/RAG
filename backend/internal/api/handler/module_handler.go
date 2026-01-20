package handler

import (
	"net/http"

	"rag-backend/internal/domain/common"
	moduleService "rag-backend/internal/service/module"

	"github.com/gin-gonic/gin"
)

// ModuleHandler 模块处理器
type ModuleHandler struct {
	service moduleService.Service
}

// NewModuleHandler 创建模块处理器实例
func NewModuleHandler(service moduleService.Service) *ModuleHandler {
	return &ModuleHandler{service: service}
}

// GetModuleTree 获取模块树
// @Summary 获取模块树
// @Tags 模块管理
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/modules/tree [get]
func (h *ModuleHandler) GetModuleTree(c *gin.Context) {
	projectID := c.Param("id")

	tree, err := h.service.GetModuleTree(projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get module tree",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tree))
}

// CreateModule 创建模块
// @Summary 创建模块
// @Tags 模块管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body moduleService.CreateModuleRequest true "创建模块请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/modules [post]
func (h *ModuleHandler) CreateModule(c *gin.Context) {
	projectID := c.Param("id")

	var req moduleService.CreateModuleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	module, err := h.service.CreateModule(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to create module",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(module))
}

// UpdateModule 更新模块
// @Summary 更新模块
// @Tags 模块管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param module_id path string true "模块ID"
// @Param request body moduleService.UpdateModuleRequest true "更新模块请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/modules/{module_id} [put]
func (h *ModuleHandler) UpdateModule(c *gin.Context) {
	moduleID := c.Param("module_id")

	var req moduleService.UpdateModuleRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	module, err := h.service.UpdateModule(moduleID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update module",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(module))
}

// DeleteModule 删除模块
// @Summary 删除模块
// @Tags 模块管理
// @Produce json
// @Param id path string true "项目ID"
// @Param module_id path string true "模块ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/modules/{module_id} [delete]
func (h *ModuleHandler) DeleteModule(c *gin.Context) {
	moduleID := c.Param("module_id")

	if err := h.service.DeleteModule(moduleID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to delete module",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Module deleted successfully",
	}))
}

// SortModules 模块排序
// @Summary 模块排序
// @Tags 模块管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body moduleService.SortModulesRequest true "排序请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/modules/sort [put]
func (h *ModuleHandler) SortModules(c *gin.Context) {
	projectID := c.Param("id")

	var req moduleService.SortModulesRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	if err := h.service.SortModules(projectID, &req); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to sort modules",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Modules sorted successfully",
	}))
}
