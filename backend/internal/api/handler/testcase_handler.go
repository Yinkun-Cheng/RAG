package handler

import (
	"fmt"
	"net/http"

	"rag-backend/internal/domain/common"
	testcaseService "rag-backend/internal/service/testcase"

	"github.com/gin-gonic/gin"
)

// TestCaseHandler 测试用例处理器
type TestCaseHandler struct {
	service testcaseService.Service
}

// NewTestCaseHandler 创建测试用例处理器实例
func NewTestCaseHandler(service testcaseService.Service) *TestCaseHandler {
	return &TestCaseHandler{service: service}
}

// CreateTestCase 创建测试用例
// @Summary 创建测试用例
// @Tags 测试用例管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body testcaseService.CreateTestCaseRequest true "创建测试用例请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases [post]
func (h *TestCaseHandler) CreateTestCase(c *gin.Context) {
	projectID := c.Param("id")

	var req testcaseService.CreateTestCaseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	tc, err := h.service.CreateTestCase(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to create test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tc))
}

// GetTestCase 获取测试用例详情
// @Summary 获取测试用例详情
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id} [get]
func (h *TestCaseHandler) GetTestCase(c *gin.Context) {
	testCaseID := c.Param("testcase_id")

	tc, err := h.service.GetTestCase(testCaseID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tc))
}

// ListTestCases 获取测试用例列表
// @Summary 获取测试用例列表
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param prd_id query string false "PRD ID"
// @Param module_id query string false "模块ID"
// @Param priority query string false "优先级"
// @Param type query string false "类型"
// @Param status query string false "状态"
// @Param app_version_id query string false "App版本ID"
// @Param tag_ids query []string false "标签ID列表"
// @Param keyword query string false "关键词"
// @Param page query int true "页码"
// @Param page_size query int true "每页数量"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases [get]
func (h *TestCaseHandler) ListTestCases(c *gin.Context) {
	projectID := c.Param("id")

	var req testcaseService.ListTestCaseRequest
	if err := c.ShouldBindQuery(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	response, err := h.service.ListTestCases(projectID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to list test cases",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(response))
}

// UpdateTestCase 更新测试用例
// @Summary 更新测试用例
// @Tags 测试用例管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Param request body testcaseService.UpdateTestCaseRequest true "更新测试用例请求"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id} [put]
func (h *TestCaseHandler) UpdateTestCase(c *gin.Context) {
	testCaseID := c.Param("testcase_id")

	var req testcaseService.UpdateTestCaseRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	tc, err := h.service.UpdateTestCase(testCaseID, &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to update test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(tc))
}

// DeleteTestCase 删除测试用例
// @Summary 删除测试用例
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id} [delete]
func (h *TestCaseHandler) DeleteTestCase(c *gin.Context) {
	testCaseID := c.Param("testcase_id")

	if err := h.service.DeleteTestCase(testCaseID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to delete test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Test case deleted successfully",
	}))
}

// BatchDeleteTestCases 批量删除测试用例
// @Summary 批量删除测试用例
// @Tags 测试用例管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param request body map[string][]string true "测试用例ID列表"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/batch-delete [post]
func (h *TestCaseHandler) BatchDeleteTestCases(c *gin.Context) {
	var req struct {
		IDs []string `json:"ids" binding:"required,min=1"`
	}
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(
			common.CodeBadRequest,
			"Invalid request parameters",
			err.Error(),
		))
		return
	}

	if err := h.service.BatchDeleteTestCases(req.IDs); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to batch delete test cases",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Test cases deleted successfully",
		"count":   len(req.IDs),
	}))
}

// AddTestCaseTag 为测试用例添加标签
// @Summary 为测试用例添加标签
// @Tags 测试用例管理
// @Accept json
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Param request body map[string]string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id}/tags [post]
func (h *TestCaseHandler) AddTestCaseTag(c *gin.Context) {
	testCaseID := c.Param("testcase_id")

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

	if err := h.service.AddTestCaseTag(testCaseID, req.TagID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to add tag to test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Tag added successfully",
	}))
}

// RemoveTestCaseTag 移除测试用例的标签
// @Summary 移除测试用例的标签
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Param tag_id path string true "标签ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id}/tags/{tag_id} [delete]
func (h *TestCaseHandler) RemoveTestCaseTag(c *gin.Context) {
	testCaseID := c.Param("testcase_id")
	tagID := c.Param("tag_id")

	if err := h.service.RemoveTestCaseTag(testCaseID, tagID); err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to remove tag from test case",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(gin.H{
		"message": "Tag removed successfully",
	}))
}


// GetTestCaseVersions 获取测试用例版本列表
// @Summary 获取测试用例版本列表
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id}/versions [get]
func (h *TestCaseHandler) GetTestCaseVersions(c *gin.Context) {
	testCaseID := c.Param("testcase_id")

	versions, err := h.service.GetTestCaseVersions(testCaseID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get test case versions",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(versions))
}

// GetTestCaseVersion 获取测试用例特定版本
// @Summary 获取测试用例特定版本
// @Tags 测试用例管理
// @Produce json
// @Param id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Param version path int true "版本号"
// @Success 200 {object} common.Response
// @Router /api/v1/projects/{id}/testcases/{testcase_id}/versions/{version} [get]
func (h *TestCaseHandler) GetTestCaseVersion(c *gin.Context) {
	testCaseID := c.Param("testcase_id")
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

	v, err := h.service.GetTestCaseVersion(testCaseID, version)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(
			common.CodeInternalServerError,
			"Failed to get test case version",
			err.Error(),
		))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(v))
}
