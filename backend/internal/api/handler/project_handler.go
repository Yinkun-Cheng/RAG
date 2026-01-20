package handler

import (
	"net/http"
	"strconv"

	"rag-backend/internal/domain/common"
	projectService "rag-backend/internal/service/project"

	"github.com/gin-gonic/gin"
)

// ProjectHandler 项目处理器
type ProjectHandler struct {
	service projectService.Service
}

// NewProjectHandler 创建项目处理器实例
func NewProjectHandler(service projectService.Service) *ProjectHandler {
	return &ProjectHandler{service: service}
}

// CreateProject 创建项目
// @Summary 创建项目
// @Tags 项目管理
// @Accept json
// @Produce json
// @Param request body projectService.CreateProjectRequest true "创建项目请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects [post]
func (h *ProjectHandler) CreateProject(c *gin.Context) {
	var req projectService.CreateProjectRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	proj, err := h.service.CreateProject(&req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to create project",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(proj))
}

// GetProject 获取项目详情
// @Summary 获取项目详情
// @Tags 项目管理
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id} [get]
func (h *ProjectHandler) GetProject(c *gin.Context) {
	id := c.Param("id")

	proj, err := h.service.GetProject(id)
	if err != nil {
		c.JSON(http.StatusNotFound, common.ErrorResponse(
			common.CodeNotFound,
			"Project not found",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(proj))
}

// ListProjects 获取项目列表
// @Summary 获取项目列表
// @Tags 项目管理
// @Produce json
// @Param page query int false "页码" default(1)
// @Param page_size query int false "每页数量" default(10)
// @Success 200 {object} common.Response
// @Router /api/v1/projects [get]
func (h *ProjectHandler) ListProjects(c *gin.Context) {
	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	pageSize, _ := strconv.Atoi(c.DefaultQuery("page_size", "10"))

	projects, total, err := h.service.ListProjects(page, pageSize)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get projects",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(common.PaginatedResponse{
		Total:    total,
		Page:     page,
		PageSize: pageSize,
		Items:    projects,
	}))
}

// UpdateProject 更新项目
// @Summary 更新项目
// @Tags 项目管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body projectService.UpdateProjectRequest true "更新项目请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id} [put]
func (h *ProjectHandler) UpdateProject(c *gin.Context) {
	id := c.Param("id")

	var req projectService.UpdateProjectRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	proj, err := h.service.UpdateProject(id, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update project",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(proj))
}

// DeleteProject 删除项目
// @Summary 删除项目
// @Tags 项目管理
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id} [delete]
func (h *ProjectHandler) DeleteProject(c *gin.Context) {
	id := c.Param("id")

	if err := h.service.DeleteProject(id); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to delete project",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Project deleted successfully",
	}))
}

// GetProjectStatistics 获取项目统计信息
// @Summary 获取项目统计信息
// @Tags 项目管理
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/statistics [get]
func (h *ProjectHandler) GetProjectStatistics(c *gin.Context) {
	id := c.Param("id")

	stats, err := h.service.GetProjectStatistics(id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get project statistics",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(stats))
}
