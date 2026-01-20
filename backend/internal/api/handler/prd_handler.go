package handler

import (
	"fmt"
	"net/http"

	"rag-backend/internal/domain/common"
	prdService "rag-backend/internal/service/prd"

	"github.com/gin-gonic/gin"
)

// PRDHandler PRD 文档处理器
type PRDHandler struct {
	service prdService.Service
}

// NewPRDHandler 创建 PRD 文档处理器实例
func NewPRDHandler(service prdService.Service) *PRDHandler {
	return &PRDHandler{service: service}
}

// CreatePRD 创建 PRD 文档
// @Summary 创建 PRD 文档
// @Tags PRD 管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body prdService.CreatePRDRequest true "创建 PRD 请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds [post]
func (h *PRDHandler) CreatePRD(c *gin.Context) {
	projectID := c.Param("id")

	var req prdService.CreatePRDRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	doc, err := h.service.CreatePRD(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to create PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// GetPRD 获取 PRD 文档详情
// @Summary 获取 PRD 文档详情
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id} [get]
func (h *PRDHandler) GetPRD(c *gin.Context) {
	prdID := c.Param("prd_id")

	doc, err := h.service.GetPRD(prdID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// ListPRDs 获取 PRD 文档列表
// @Summary 获取 PRD 文档列表
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param module_id query string false "模块ID"
// @Param status query string false "状态"
// @Param app_version_id query string false "App版本ID"
// @Param tag_ids query []string false "标签ID列表"
// @Param keyword query string false "关键词"
// @Param page query int true "页码"
// @Param page_size query int true "每页数量"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds [get]
func (h *PRDHandler) ListPRDs(c *gin.Context) {
	projectID := c.Param("id")

	var req prdService.ListPRDRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	response, err := h.service.ListPRDs(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to list PRDs",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(response))
}

// UpdatePRD 更新 PRD 文档
// @Summary 更新 PRD 文档
// @Tags PRD 管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param request body prdService.UpdatePRDRequest true "更新 PRD 请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id} [put]
func (h *PRDHandler) UpdatePRD(c *gin.Context) {
	prdID := c.Param("prd_id")

	var req prdService.UpdatePRDRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	doc, err := h.service.UpdatePRD(prdID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// DeletePRD 删除 PRD 文档
// @Summary 删除 PRD 文档
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id} [delete]
func (h *PRDHandler) DeletePRD(c *gin.Context) {
	prdID := c.Param("prd_id")

	if err := h.service.DeletePRD(prdID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to delete PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "PRD deleted successfully",
	}))
}


// GetPRDVersions 获取 PRD 版本列表
// @Summary 获取 PRD 版本列表
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/versions [get]
func (h *PRDHandler) GetPRDVersions(c *gin.Context) {
	prdID := c.Param("prd_id")

	versions, err := h.service.GetPRDVersions(prdID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get PRD versions",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(versions))
}

// GetPRDVersion 获取 PRD 特定版本
// @Summary 获取 PRD 特定版本
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param version path int true "版本号"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/versions/{version} [get]
func (h *PRDHandler) GetPRDVersion(c *gin.Context) {
	prdID := c.Param("prd_id")
	versionStr := c.Param("version")

	var version int
	if _, err := fmt.Sscanf(versionStr, "%d", &version); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid version number",
			err.Error(),
		))
		return
	}

	v, err := h.service.GetPRDVersion(prdID, version)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get PRD version",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(v))
}

// ComparePRDVersions 对比 PRD 版本
// @Summary 对比 PRD 版本
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param version1 query int true "版本1"
// @Param version2 query int true "版本2"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/versions/compare [get]
func (h *PRDHandler) ComparePRDVersions(c *gin.Context) {
	prdID := c.Param("prd_id")
	
	var version1, version2 int
	if _, err := fmt.Sscanf(c.Query("version1"), "%d", &version1); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid version1 number",
			err.Error(),
		))
		return
	}
	if _, err := fmt.Sscanf(c.Query("version2"), "%d", &version2); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid version2 number",
			err.Error(),
		))
		return
	}

	result, err := h.service.ComparePRDVersions(prdID, version1, version2)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to compare PRD versions",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(result))
}


// UpdatePRDStatus 更新 PRD 状态
// @Summary 更新 PRD 状态
// @Tags PRD 管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param request body map[string]string true "状态更新请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/status [put]
func (h *PRDHandler) UpdatePRDStatus(c *gin.Context) {
	prdID := c.Param("prd_id")

	var req struct {
		Status string `json:"status" binding:"required,oneof=draft published archived"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	doc, err := h.service.UpdatePRDStatus(prdID, req.Status)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update PRD status",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// PublishPRD 发布 PRD
// @Summary 发布 PRD
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/publish [post]
func (h *PRDHandler) PublishPRD(c *gin.Context) {
	prdID := c.Param("prd_id")

	doc, err := h.service.PublishPRD(prdID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to publish PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// ArchivePRD 归档 PRD
// @Summary 归档 PRD
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/archive [post]
func (h *PRDHandler) ArchivePRD(c *gin.Context) {
	prdID := c.Param("prd_id")

	doc, err := h.service.ArchivePRD(prdID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to archive PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(doc))
}

// AddPRDTag 为 PRD 添加标签
// @Summary 为 PRD 添加标签
// @Tags PRD 管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param request body map[string]string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/tags [post]
func (h *PRDHandler) AddPRDTag(c *gin.Context) {
	prdID := c.Param("prd_id")

	var req struct {
		TagID string `json:"tag_id" binding:"required"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	if err := h.service.AddPRDTag(prdID, req.TagID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to add tag to PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Tag added successfully",
	}))
}

// RemovePRDTag 移除 PRD 的标签
// @Summary 移除 PRD 的标签
// @Tags PRD 管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param tag_id path string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/prds/{prd_id}/tags/{tag_id} [delete]
func (h *PRDHandler) RemovePRDTag(c *gin.Context) {
	prdID := c.Param("prd_id")
	tagID := c.Param("tag_id")

	if err := h.service.RemovePRDTag(prdID, tagID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to remove tag from PRD",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Tag removed successfully",
	}))
}
