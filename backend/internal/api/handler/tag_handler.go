package handler

import (
	"net/http"

	"rag-backend/internal/domain/common"
	tagService "rag-backend/internal/service/tag"

	"github.com/gin-gonic/gin"
)

// TagHandler 标签处理器
type TagHandler struct {
	service tagService.Service
}

// NewTagHandler 创建标签处理器实例
func NewTagHandler(service tagService.Service) *TagHandler {
	return &TagHandler{service: service}
}

// GetTags 获取所有标签
// @Summary 获取所有标签
// @Tags 标签管理
// @Produce json
// @Param id path string true "项目ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/tags [get]
func (h *TagHandler) GetTags(c *gin.Context) {
	projectID := c.Param("id")

	tags, err := h.service.GetTags(projectID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get tags",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tags))
}

// CreateTag 创建标签
// @Summary 创建标签
// @Tags 标签管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body tagService.CreateTagRequest true "创建标签请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/tags [post]
func (h *TagHandler) CreateTag(c *gin.Context) {
	projectID := c.Param("id")

	var req tagService.CreateTagRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	tag, err := h.service.CreateTag(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to create tag",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tag))
}

// UpdateTag 更新标签
// @Summary 更新标签
// @Tags 标签管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param tag_id path string true "标签ID"
// @Param request body tagService.UpdateTagRequest true "更新标签请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/tags/{tag_id} [put]
func (h *TagHandler) UpdateTag(c *gin.Context) {
	tagID := c.Param("tag_id")

	var req tagService.UpdateTagRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	tag, err := h.service.UpdateTag(tagID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update tag",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tag))
}

// DeleteTag 删除标签
// @Summary 删除标签
// @Tags 标签管理
// @Produce json
// @Param id path string true "项目ID"
// @Param tag_id path string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/tags/{tag_id} [delete]
func (h *TagHandler) DeleteTag(c *gin.Context) {
	tagID := c.Param("tag_id")

	if err := h.service.DeleteTag(tagID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to delete tag",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Tag deleted successfully",
	}))
}

// GetTagUsage 获取标签使用统计
// @Summary 获取标签使用统计
// @Tags 标签管理
// @Produce json
// @Param id path string true "项目ID"
// @Param tag_id path string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/tags/{tag_id}/usage [get]
func (h *TagHandler) GetTagUsage(c *gin.Context) {
	tagID := c.Param("tag_id")

	usage, err := h.service.GetTagUsage(tagID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get tag usage",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(usage))
}
