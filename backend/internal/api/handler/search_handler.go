package handler

import (
	"net/http"
	"strconv"
	"rag-backend/internal/domain/common"
	"rag-backend/internal/service/search"

	"github.com/gin-gonic/gin"
)

// SearchHandler 搜索处理器
type SearchHandler struct {
	searchService *search.SearchService
}

// NewSearchHandler 创建搜索处理器
func NewSearchHandler(searchService *search.SearchService) *SearchHandler {
	return &SearchHandler{
		searchService: searchService,
	}
}

// Search 语义搜索
// @Summary 语义搜索
// @Description 使用自然语言搜索 PRD 和测试用例
// @Tags Search
// @Accept json
// @Produce json
// @Param project_id path string true "项目ID"
// @Param request body search.SearchRequest true "搜索请求"
// @Success 200 {object} common.Response{data=search.SearchResponse}
// @Router /api/v1/projects/{project_id}/search [post]
func (h *SearchHandler) Search(c *gin.Context) {
	projectID := c.Param("id")

	var req search.SearchRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, common.ErrorResponse(http.StatusBadRequest, "参数错误", err.Error()))
		return
	}

	// 设置项目ID
	req.ProjectID = projectID

	// 执行搜索
	result, err := h.searchService.Search(c.Request.Context(), &req)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "搜索失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(result))
}

// GetPRDRecommendations 获取 PRD 推荐
// @Summary 获取 PRD 相关推荐
// @Description 基于指定 PRD 获取相关推荐
// @Tags Search
// @Accept json
// @Produce json
// @Param project_id path string true "项目ID"
// @Param prd_id path string true "PRD ID"
// @Param limit query int false "结果数量限制" default(5)
// @Success 200 {object} common.Response{data=search.SearchResponse}
// @Router /api/v1/projects/{project_id}/prds/{prd_id}/recommendations [get]
func (h *SearchHandler) GetPRDRecommendations(c *gin.Context) {
	projectID := c.Param("id")
	prdID := c.Param("prd_id")

	// 获取查询参数
	limit := 5
	if limitStr := c.Query("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
			limit = l
		}
	}

	// 执行推荐
	result, err := h.searchService.GetRecommendations(c.Request.Context(), projectID, "prd", prdID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "获取 PRD 推荐失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(result))
}

// GetTestCaseRecommendations 获取测试用例推荐
// @Summary 获取测试用例相关推荐
// @Description 基于指定测试用例获取相关推荐
// @Tags Search
// @Accept json
// @Produce json
// @Param project_id path string true "项目ID"
// @Param testcase_id path string true "测试用例ID"
// @Param limit query int false "结果数量限制" default(5)
// @Success 200 {object} common.Response{data=search.SearchResponse}
// @Router /api/v1/projects/{project_id}/testcases/{testcase_id}/recommendations [get]
func (h *SearchHandler) GetTestCaseRecommendations(c *gin.Context) {
	projectID := c.Param("id")
	testcaseID := c.Param("testcase_id")

	// 获取查询参数
	limit := 5
	if limitStr := c.Query("limit"); limitStr != "" {
		if l, err := strconv.Atoi(limitStr); err == nil && l > 0 {
			limit = l
		}
	}

	// 执行推荐
	result, err := h.searchService.GetRecommendations(c.Request.Context(), projectID, "testcase", testcaseID, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, common.ErrorResponse(http.StatusInternalServerError, "获取测试用例推荐失败", err.Error()))
		return
	}

	c.JSON(http.StatusOK, common.SuccessResponse(result))
}
